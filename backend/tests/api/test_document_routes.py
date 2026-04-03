from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import event

from app.api import document_routes
from app.models.locataire import Locataire
from app.models.document import Document, TypeDocument
from app.models.sci import SCI
from app.models.user import UserRole
from app.utils.auth import CurrentUser, get_current_user
from app.utils.db import get_db


def test_documents_library_supports_folder_creation_and_free_upload(monkeypatch, db_session):
    app = FastAPI()
    app.include_router(document_routes.router)

    sci = SCI(nom="SCI Documents")
    db_session.add(sci)
    db_session.commit()
    db_session.refresh(sci)

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_current_user():
        return CurrentUser(id=1, role=UserRole.ADMIN, is_active=True)

    monkeypatch.setattr("app.api.document_routes.upload_bytes", lambda **kwargs: "http://minio/documents/file.pdf")

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_current_user

    try:
        with TestClient(app) as client:
            create_folder = client.post(
                "/api/documents/folders",
                json={"sci_id": sci.id, "nom": "Baux signés"},
            )
            assert create_folder.status_code == 201
            folder = create_folder.json()
            assert folder["nom"] == "Baux signés"

            root_library = client.get("/api/documents/library", params={"sci_id": sci.id})
            assert root_library.status_code == 200
            assert len(root_library.json()["folders"]) == 1
            assert root_library.json()["documents"] == []

            upload = client.post(
                "/api/documents/upload",
                data={
                    "sci_id": str(sci.id),
                    "folder_id": str(folder["id"]),
                    "nom_document": "Bail locataire mars 2026",
                    "type_document": "autre",
                },
                files={"file": ("bail-original.pdf", b"fake-pdf-content", "application/pdf")},
            )
            assert upload.status_code == 201
            uploaded_document = upload.json()
            assert uploaded_document["nom_fichier"] == "Bail locataire mars 2026.pdf"
            assert uploaded_document["folder_id"] == folder["id"]

            folder_library = client.get("/api/documents/library", params={"folder_id": folder["id"]})
            assert folder_library.status_code == 200
            payload = folder_library.json()
            assert payload["current_folder"]["id"] == folder["id"]
            assert payload["folders"] == []
            assert len(payload["documents"]) == 1
    finally:
        app.dependency_overrides.clear()


def test_delete_document_removes_storage_object_before_deleting_row(monkeypatch, db_session):
    app = FastAPI()
    app.include_router(document_routes.router)

    sci = SCI(nom="SCI Suppression")
    db_session.add(sci)
    db_session.commit()
    db_session.refresh(sci)

    document = Document(
        sci_id=sci.id,
        type_document=TypeDocument.AUTRE,
        s3_url="http://minio/documents/folders/12/document.pdf",
        nom_fichier="document.pdf",
    )
    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)

    deleted_urls: list[str] = []

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_current_user():
        return CurrentUser(id=1, role=UserRole.ADMIN, is_active=True)

    monkeypatch.setattr("app.api.document_routes.delete_object_by_url", deleted_urls.append)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_current_user

    try:
        with TestClient(app) as client:
            response = client.delete(f"/api/documents/{document.id}")
            assert response.status_code == 204
            assert deleted_urls == ["http://minio/documents/folders/12/document.pdf"]
            assert db_session.get(Document, document.id) is None
    finally:
        app.dependency_overrides.clear()


def test_locataire_documents_checklist_uses_grouped_count_query(db_session):
    app = FastAPI()
    app.include_router(document_routes.router)

    sci = SCI(nom="SCI Checklist")
    db_session.add(sci)
    db_session.flush()

    locataire = Locataire(nom="Checklist", prenom="Client", email="checklist@example.com")
    db_session.add(locataire)
    db_session.flush()

    db_session.add_all(
        [
            Document(
                sci_id=sci.id,
                locataire_id=locataire.id,
                type_document=TypeDocument.PIECE_IDENTITE,
                s3_url="http://minio/documents/piece-1.pdf",
                nom_fichier="piece-1.pdf",
            ),
            Document(
                sci_id=sci.id,
                locataire_id=locataire.id,
                type_document=TypeDocument.PIECE_IDENTITE,
                s3_url="http://minio/documents/piece-2.pdf",
                nom_fichier="piece-2.pdf",
            ),
            Document(
                sci_id=sci.id,
                locataire_id=locataire.id,
                type_document=TypeDocument.RIB,
                s3_url="http://minio/documents/rib.pdf",
                nom_fichier="rib.pdf",
            ),
        ]
    )
    db_session.commit()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_current_user():
        return CurrentUser(id=1, role=UserRole.ADMIN, is_active=True)

    sql_statements: list[str] = []

    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        sql_statements.append(statement)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_current_user

    event.listen(db_session.bind, "before_cursor_execute", before_cursor_execute)
    try:
        with TestClient(app) as client:
            response = client.get(f"/api/documents/locataire/{locataire.id}/checklist")
            assert response.status_code == 200
            payload = response.json()
            items_by_type = {item["type_document"]: item for item in payload["items"]}

            assert items_by_type["piece_identite"]["uploaded_count"] == 2
            assert items_by_type["rib"]["uploaded_count"] == 1
            assert items_by_type["piece_identite"]["is_complete"] is True
            assert any("GROUP BY" in statement.upper() and "COUNT(" in statement.upper() for statement in sql_statements)
    finally:
        event.remove(db_session.bind, "before_cursor_execute", before_cursor_execute)
        app.dependency_overrides.clear()

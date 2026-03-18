'use client'

import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { biensApi, type Bien, type BienCreate, TypeBien, StatutBien, ClasseDPE, TYPE_BIEN_LABELS, STATUT_BIEN_LABELS, CLASSE_DPE_LABELS } from '@/lib/api/biens'
import { sciApi, type SCI } from '@/lib/api/sci'
import { toast } from 'sonner'

const bienFormSchema = z.object({
  sci_id: z.string().min(1, 'La SCI est requise'),
  adresse: z.string().min(1, 'L\'adresse est requise'),
  ville: z.string().min(1, 'La ville est requise').max(100),
  code_postal: z.string().length(5, 'Le code postal doit contenir 5 chiffres'),
  complement_adresse: z.string().optional(),
  type_bien: z.nativeEnum(TypeBien, { required_error: 'Le type de bien est requis' }),
  surface: z.string().optional(),
  nb_pieces: z.string().optional(),
  etage: z.string().optional(),
  date_acquisition: z.string().optional(),
  prix_acquisition: z.string().optional(),
  valeur_actuelle: z.string().optional(),
  dpe_classe: z.nativeEnum(ClasseDPE).optional(),
  dpe_date_validite: z.string().optional(),
  statut: z.nativeEnum(StatutBien, { required_error: 'Le statut est requis' }),
})

type BienFormData = z.infer<typeof bienFormSchema>

interface BienFormDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess: () => void
  bien?: Bien
}

export function BienFormDialog({ open, onOpenChange, onSuccess, bien }: BienFormDialogProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [scis, setScis] = useState<SCI[]>([])
  const isEditing = !!bien

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setValue,
    watch,
  } = useForm<BienFormData>({
    resolver: zodResolver(bienFormSchema),
    defaultValues: bien ? {
      sci_id: bien.sci_id.toString(),
      adresse: bien.adresse,
      ville: bien.ville,
      code_postal: bien.code_postal,
      complement_adresse: bien.complement_adresse || '',
      type_bien: bien.type_bien,
      surface: bien.surface?.toString() || '',
      nb_pieces: bien.nb_pieces?.toString() || '',
      etage: bien.etage?.toString() || '',
      date_acquisition: bien.date_acquisition || '',
      prix_acquisition: bien.prix_acquisition?.toString() || '',
      valeur_actuelle: bien.valeur_actuelle?.toString() || '',
      dpe_classe: bien.dpe_classe,
      dpe_date_validite: bien.dpe_date_validite || '',
      statut: bien.statut,
    } : {
      statut: StatutBien.VACANT,
    },
  })

  const typeBien = watch('type_bien')
  const statut = watch('statut')
  const dpeClasse = watch('dpe_classe')

  useEffect(() => {
    const loadSCIs = async () => {
      try {
        const data = await sciApi.getAll()
        setScis(data)
      } catch (error) {
        console.error('Error loading SCIs:', error)
        toast.error('Erreur lors du chargement des SCI')
      }
    }
    if (open) {
      loadSCIs()
    }
  }, [open])

  const onSubmit = async (data: BienFormData) => {
    try {
      setIsSubmitting(true)

      const payload: BienCreate = {
        sci_id: parseInt(data.sci_id),
        adresse: data.adresse,
        ville: data.ville,
        code_postal: data.code_postal,
        complement_adresse: data.complement_adresse || undefined,
        type_bien: data.type_bien,
        surface: data.surface ? parseFloat(data.surface) : undefined,
        nb_pieces: data.nb_pieces ? parseInt(data.nb_pieces) : undefined,
        etage: data.etage ? parseInt(data.etage) : undefined,
        date_acquisition: data.date_acquisition || undefined,
        prix_acquisition: data.prix_acquisition ? parseFloat(data.prix_acquisition) : undefined,
        valeur_actuelle: data.valeur_actuelle ? parseFloat(data.valeur_actuelle) : undefined,
        dpe_classe: data.dpe_classe || undefined,
        dpe_date_validite: data.dpe_date_validite || undefined,
        statut: data.statut,
      }

      if (isEditing) {
        await biensApi.update(bien.id, payload)
        toast.success('Bien mis à jour avec succès')
      } else {
        await biensApi.create(payload)
        toast.success('Bien créé avec succès')
      }

      reset()
      onOpenChange(false)
      onSuccess()
    } catch (error: any) {
      console.error('Error saving bien:', error)
      toast.error(error.response?.data?.detail || 'Erreur lors de la sauvegarde')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{isEditing ? 'Modifier le bien' : 'Nouveau bien immobilier'}</DialogTitle>
          <DialogDescription>
            {isEditing
              ? 'Modifiez les informations du bien'
              : 'Remplissez les informations pour créer un nouveau bien'}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div className="grid gap-6">
            {/* SCI */}
            <div className="space-y-2">
              <Label htmlFor="sci_id">
                SCI <span className="text-destructive">*</span>
              </Label>
              <Select
                onValueChange={(value) => setValue('sci_id', value, { shouldValidate: true })}
                value={watch('sci_id')}
              >
                <SelectTrigger className={errors.sci_id ? 'border-destructive' : ''}>
                  <SelectValue placeholder="Sélectionnez une SCI" />
                </SelectTrigger>
                <SelectContent>
                  {scis.map((sci) => (
                    <SelectItem key={sci.id} value={sci.id.toString()}>
                      {sci.nom}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.sci_id && (
                <p className="text-sm text-destructive">{errors.sci_id.message}</p>
              )}
            </div>

            {/* Type & Statut */}
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="type_bien">
                  Type de bien <span className="text-destructive">*</span>
                </Label>
                <Select
                  onValueChange={(value) => setValue('type_bien', value as TypeBien, { shouldValidate: true })}
                  value={typeBien}
                >
                  <SelectTrigger className={errors.type_bien ? 'border-destructive' : ''}>
                    <SelectValue placeholder="Sélectionnez un type" />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(TYPE_BIEN_LABELS).map(([value, label]) => (
                      <SelectItem key={value} value={value}>
                        {label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.type_bien && (
                  <p className="text-sm text-destructive">{errors.type_bien.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="statut">
                  Statut <span className="text-destructive">*</span>
                </Label>
                <Select
                  onValueChange={(value) => setValue('statut', value as StatutBien, { shouldValidate: true })}
                  value={statut}
                >
                  <SelectTrigger className={errors.statut ? 'border-destructive' : ''}>
                    <SelectValue placeholder="Sélectionnez un statut" />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(STATUT_BIEN_LABELS).map(([value, label]) => (
                      <SelectItem key={value} value={value}>
                        {label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.statut && (
                  <p className="text-sm text-destructive">{errors.statut.message}</p>
                )}
              </div>
            </div>

            {/* Adresse */}
            <div className="space-y-2">
              <Label htmlFor="adresse">
                Adresse <span className="text-destructive">*</span>
              </Label>
              <Input
                id="adresse"
                {...register('adresse')}
                placeholder="15 Avenue de la République"
                className={errors.adresse ? 'border-destructive' : ''}
              />
              {errors.adresse && (
                <p className="text-sm text-destructive">{errors.adresse.message}</p>
              )}
            </div>

            {/* Complément adresse */}
            <div className="space-y-2">
              <Label htmlFor="complement_adresse">Complément d'adresse</Label>
              <Input
                id="complement_adresse"
                {...register('complement_adresse')}
                placeholder="Appartement 3B, Bâtiment A"
              />
            </div>

            {/* Ville & Code postal */}
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="ville">
                  Ville <span className="text-destructive">*</span>
                </Label>
                <Input
                  id="ville"
                  {...register('ville')}
                  placeholder="Paris"
                  className={errors.ville ? 'border-destructive' : ''}
                />
                {errors.ville && (
                  <p className="text-sm text-destructive">{errors.ville.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="code_postal">
                  Code postal <span className="text-destructive">*</span>
                </Label>
                <Input
                  id="code_postal"
                  {...register('code_postal')}
                  placeholder="75011"
                  maxLength={5}
                  className={errors.code_postal ? 'border-destructive' : ''}
                />
                {errors.code_postal && (
                  <p className="text-sm text-destructive">{errors.code_postal.message}</p>
                )}
              </div>
            </div>

            {/* Surface, Pièces & Étage */}
            <div className="grid gap-4 sm:grid-cols-3">
              <div className="space-y-2">
                <Label htmlFor="surface">Surface (m²)</Label>
                <Input
                  id="surface"
                  type="number"
                  step="0.01"
                  {...register('surface')}
                  placeholder="45.5"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="nb_pieces">Nombre de pièces</Label>
                <Input
                  id="nb_pieces"
                  type="number"
                  {...register('nb_pieces')}
                  placeholder="3"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="etage">Étage</Label>
                <Input
                  id="etage"
                  type="number"
                  {...register('etage')}
                  placeholder="2"
                />
              </div>
            </div>

            {/* Date acquisition & Prix */}
            <div className="grid gap-4 sm:grid-cols-3">
              <div className="space-y-2">
                <Label htmlFor="date_acquisition">Date d'acquisition</Label>
                <Input
                  id="date_acquisition"
                  type="date"
                  {...register('date_acquisition')}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="prix_acquisition">Prix d'acquisition (€)</Label>
                <Input
                  id="prix_acquisition"
                  type="number"
                  step="0.01"
                  {...register('prix_acquisition')}
                  placeholder="250000"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="valeur_actuelle">Valeur actuelle (€)</Label>
                <Input
                  id="valeur_actuelle"
                  type="number"
                  step="0.01"
                  {...register('valeur_actuelle')}
                  placeholder="280000"
                />
              </div>
            </div>

            {/* DPE */}
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="dpe_classe">Classe DPE</Label>
                <Select
                  onValueChange={(value) => setValue('dpe_classe', value as ClasseDPE)}
                  value={dpeClasse}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionnez une classe" />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(CLASSE_DPE_LABELS).map(([value, label]) => (
                      <SelectItem key={value} value={value}>
                        {label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="dpe_date_validite">Date validité DPE</Label>
                <Input
                  id="dpe_date_validite"
                  type="date"
                  {...register('dpe_date_validite')}
                />
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isSubmitting}
            >
              Annuler
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Enregistrement...' : isEditing ? 'Mettre à jour' : 'Créer'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

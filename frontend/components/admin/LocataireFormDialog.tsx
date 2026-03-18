'use client'

import { useState } from 'react'
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
import { locatairesApi, type Locataire, type LocataireCreate } from '@/lib/api/locataires'
import { toast } from 'sonner'

const locataireFormSchema = z.object({
  nom: z.string().min(1, 'Le nom est requis').max(100),
  prenom: z.string().min(1, 'Le prénom est requis').max(100),
  email: z.string().email('Email invalide').max(200),
  telephone: z.string().min(6, 'Téléphone invalide').max(20),
  date_naissance: z.string().min(1, 'La date de naissance est requise'),
  profession: z.string().min(1, 'La profession est requise').max(200),
  revenus_annuels: z.string().min(1, 'Les revenus annuels sont requis'),
})

type LocataireFormData = z.infer<typeof locataireFormSchema>

interface LocataireFormDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess: () => void
  locataire?: Locataire
}

export function LocataireFormDialog({ open, onOpenChange, onSuccess, locataire }: LocataireFormDialogProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const isEditing = !!locataire

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<LocataireFormData>({
    resolver: zodResolver(locataireFormSchema),
    defaultValues: locataire ? {
      nom: locataire.nom,
      prenom: locataire.prenom,
      email: locataire.email || '',
      telephone: locataire.telephone || '',
      date_naissance: locataire.date_naissance || '',
      profession: locataire.profession || '',
      revenus_annuels: locataire.revenus_annuels?.toString() || '',
    } : {},
  })

  const onSubmit = async (data: LocataireFormData) => {
    try {
      setIsSubmitting(true)

      const payload: LocataireCreate = {
        nom: data.nom,
        prenom: data.prenom,
        email: data.email,
        telephone: data.telephone,
        date_naissance: data.date_naissance,
        profession: data.profession,
        revenus_annuels: parseFloat(data.revenus_annuels),
      }

      if (isEditing) {
        await locatairesApi.update(locataire.id, payload)
        toast.success('Locataire mis à jour avec succès')
      } else {
        await locatairesApi.create(payload)
        toast.success('Locataire créé avec succès')
      }

      reset()
      onOpenChange(false)
      onSuccess()
    } catch (error: any) {
      console.error('Error saving locataire:', error)
      toast.error(error.response?.data?.detail || 'Erreur lors de la sauvegarde')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{isEditing ? 'Modifier le locataire' : 'Nouveau locataire'}</DialogTitle>
          <DialogDescription>
            {isEditing
              ? 'Modifiez les informations du locataire'
              : 'Remplissez les informations pour créer un nouveau locataire'}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div className="grid gap-6">
            {/* Nom & Prénom */}
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="nom">
                  Nom <span className="text-destructive">*</span>
                </Label>
                <Input
                  id="nom"
                  {...register('nom')}
                  placeholder="Dupont"
                  className={errors.nom ? 'border-destructive' : ''}
                />
                {errors.nom && (
                  <p className="text-sm text-destructive">{errors.nom.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="prenom">
                  Prénom <span className="text-destructive">*</span>
                </Label>
                <Input
                  id="prenom"
                  {...register('prenom')}
                  placeholder="Marie"
                  className={errors.prenom ? 'border-destructive' : ''}
                />
                {errors.prenom && (
                  <p className="text-sm text-destructive">{errors.prenom.message}</p>
                )}
              </div>
            </div>

            {/* Email & Téléphone */}
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="email">
                  Email <span className="text-destructive">*</span>
                </Label>
                <Input
                  id="email"
                  type="email"
                  {...register('email')}
                  placeholder="marie.dupont@email.com"
                  className={errors.email ? 'border-destructive' : ''}
                />
                {errors.email && (
                  <p className="text-sm text-destructive">{errors.email.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="telephone">
                  Téléphone <span className="text-destructive">*</span>
                </Label>
                <Input
                  id="telephone"
                  type="tel"
                  {...register('telephone')}
                  placeholder="06 12 34 56 78"
                  className={errors.telephone ? 'border-destructive' : ''}
                />
                {errors.telephone && (
                  <p className="text-sm text-destructive">{errors.telephone.message}</p>
                )}
              </div>
            </div>

            {/* Date de naissance */}
            <div className="space-y-2">
              <Label htmlFor="date_naissance">
                Date de naissance <span className="text-destructive">*</span>
              </Label>
              <Input
                id="date_naissance"
                type="date"
                {...register('date_naissance')}
                className={errors.date_naissance ? 'border-destructive' : ''}
              />
              {errors.date_naissance && (
                <p className="text-sm text-destructive">{errors.date_naissance.message}</p>
              )}
            </div>

            {/* Profession & Revenus */}
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="profession">
                  Profession <span className="text-destructive">*</span>
                </Label>
                <Input
                  id="profession"
                  {...register('profession')}
                  placeholder="Ingénieur"
                  className={errors.profession ? 'border-destructive' : ''}
                />
                {errors.profession && (
                  <p className="text-sm text-destructive">{errors.profession.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="revenus_annuels">
                  Revenus annuels (€) <span className="text-destructive">*</span>
                </Label>
                <Input
                  id="revenus_annuels"
                  type="number"
                  step="0.01"
                  {...register('revenus_annuels')}
                  placeholder="35000"
                  className={errors.revenus_annuels ? 'border-destructive' : ''}
                />
                {errors.revenus_annuels && (
                  <p className="text-sm text-destructive">{errors.revenus_annuels.message}</p>
                )}
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

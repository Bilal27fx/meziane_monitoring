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
import { sciApi, type SCI, type SCICreate } from '@/lib/api/sci'
import { toast } from 'sonner'

const sciFormSchema = z.object({
  nom: z.string().min(1, 'Le nom est requis').max(200),
  forme_juridique: z.string().default('SCI'),
  siret: z.string().length(14, 'Le SIRET doit contenir 14 chiffres').optional().or(z.literal('')),
  date_creation: z.string().optional(),
  capital: z.string().optional(),
  siege_social: z.string().optional(),
  gerant_nom: z.string().max(200).optional(),
  gerant_prenom: z.string().max(200).optional(),
})

type SCIFormData = z.infer<typeof sciFormSchema>

interface SCIFormDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess: () => void
  sci?: SCI
}

export function SCIFormDialog({ open, onOpenChange, onSuccess, sci }: SCIFormDialogProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const isEditing = !!sci

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<SCIFormData>({
    resolver: zodResolver(sciFormSchema),
    defaultValues: sci ? {
      nom: sci.nom,
      forme_juridique: sci.forme_juridique || 'SCI',
      siret: sci.siret || '',
      date_creation: sci.date_creation || '',
      capital: sci.capital?.toString() || '',
      siege_social: sci.siege_social || '',
      gerant_nom: sci.gerant_nom || '',
      gerant_prenom: sci.gerant_prenom || '',
    } : {
      forme_juridique: 'SCI',
    },
  })

  const onSubmit = async (data: SCIFormData) => {
    try {
      setIsSubmitting(true)

      const payload: SCICreate = {
        nom: data.nom,
        forme_juridique: data.forme_juridique || 'SCI',
        siret: data.siret || undefined,
        date_creation: data.date_creation || undefined,
        capital: data.capital ? parseFloat(data.capital) : undefined,
        siege_social: data.siege_social || undefined,
        gerant_nom: data.gerant_nom || undefined,
        gerant_prenom: data.gerant_prenom || undefined,
      }

      if (isEditing) {
        await sciApi.update(sci.id, payload)
        toast.success('SCI mise à jour avec succès')
      } else {
        await sciApi.create(payload)
        toast.success('SCI créée avec succès')
      }

      reset()
      onOpenChange(false)
      onSuccess()
    } catch (error: any) {
      console.error('Error saving SCI:', error)
      toast.error(error.response?.data?.detail || 'Erreur lors de la sauvegarde')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{isEditing ? 'Modifier la SCI' : 'Nouvelle SCI'}</DialogTitle>
          <DialogDescription>
            {isEditing
              ? 'Modifiez les informations de la SCI'
              : 'Remplissez les informations pour créer une nouvelle SCI'}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div className="grid gap-6">
            {/* Nom */}
            <div className="space-y-2">
              <Label htmlFor="nom">
                Nom de la SCI <span className="text-destructive">*</span>
              </Label>
              <Input
                id="nom"
                {...register('nom')}
                placeholder="SCI Meziane Invest"
                className={errors.nom ? 'border-destructive' : ''}
              />
              {errors.nom && (
                <p className="text-sm text-destructive">{errors.nom.message}</p>
              )}
            </div>

            {/* Forme juridique & SIRET */}
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="forme_juridique">Forme juridique</Label>
                <Input
                  id="forme_juridique"
                  {...register('forme_juridique')}
                  placeholder="SCI"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="siret">SIRET</Label>
                <Input
                  id="siret"
                  {...register('siret')}
                  placeholder="12345678901234"
                  maxLength={14}
                  className={errors.siret ? 'border-destructive' : ''}
                />
                {errors.siret && (
                  <p className="text-sm text-destructive">{errors.siret.message}</p>
                )}
              </div>
            </div>

            {/* Date création & Capital */}
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="date_creation">Date de création</Label>
                <Input
                  id="date_creation"
                  type="date"
                  {...register('date_creation')}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="capital">Capital (€)</Label>
                <Input
                  id="capital"
                  type="number"
                  step="0.01"
                  {...register('capital')}
                  placeholder="1000"
                />
              </div>
            </div>

            {/* Siège social */}
            <div className="space-y-2">
              <Label htmlFor="siege_social">Siège social</Label>
              <Input
                id="siege_social"
                {...register('siege_social')}
                placeholder="123 Avenue de la République, 75011 Paris"
              />
            </div>

            {/* Gérant */}
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="gerant_nom">Nom du gérant</Label>
                <Input
                  id="gerant_nom"
                  {...register('gerant_nom')}
                  placeholder="Meziane"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="gerant_prenom">Prénom du gérant</Label>
                <Input
                  id="gerant_prenom"
                  {...register('gerant_prenom')}
                  placeholder="Bilal"
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

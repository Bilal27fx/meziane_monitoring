/**
 * Calculate monthly mortgage payment (mensualité)
 * @param prix - Purchase price in euros
 * @param apport - Down payment in euros
 * @param taux - Annual interest rate in percent (e.g. 3.5 for 3.5%)
 * @param duree - Loan duration in years (default 20)
 */
export function calcMensualite(
  prix: number,
  apport: number,
  taux: number,
  duree = 20
): number {
  const principal = prix - apport
  const tauxMensuel = taux / 100 / 12
  const n = duree * 12
  if (tauxMensuel === 0) return principal / n
  return (
    (principal * tauxMensuel * Math.pow(1 + tauxMensuel, n)) /
    (Math.pow(1 + tauxMensuel, n) - 1)
  )
}

/**
 * Calculate gross yield (TRI brut)
 * @param loyer - Monthly rent
 * @param prix - Purchase price
 */
export function calcTriBrut(loyer: number, prix: number): number {
  return (loyer * 12 / prix) * 100
}

/**
 * Calculate net yield (TRI net)
 * @param cashflowMensuel - Monthly net cashflow
 * @param prix - Purchase price
 */
export function calcTriNet(cashflowMensuel: number, prix: number): number {
  return (cashflowMensuel * 12 / prix) * 100
}

/**
 * Calculate monthly cashflow
 * @param loyer - Monthly rent
 * @param mensualite - Monthly mortgage payment
 * @param charges - Monthly charges/expenses
 */
export function calcCashflow(
  loyer: number,
  mensualite: number,
  charges: number
): number {
  return loyer - mensualite - charges
}

/**
 * Estimate monthly rent from purchase price
 * Uses 0.55% rule as default
 */
export function estimateLoyer(prix: number, ratio = 0.0055): number {
  return prix * ratio
}

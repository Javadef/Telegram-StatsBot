export function randomInt(min: number, max: number): number {
  return Math.floor(Math.random() * (max - min + 1)) + min
}

export function randomFrom<T>(array: T[]): T {
  return array[Math.floor(Math.random() * array.length)]!
}

/**
 * Format date to YYYY-MM-DD string WITHOUT timezone conversion
 * This ensures the date stays the same regardless of browser timezone
 * 
 * CRITICAL: Do NOT use date.toISOString().split('T')[0] as it converts to UTC!
 * This can shift dates by ±1 day depending on browser timezone.
 * 
 * @param date Date object to format
 * @returns Date string in YYYY-MM-DD format
 */
export function formatDateForAPI(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

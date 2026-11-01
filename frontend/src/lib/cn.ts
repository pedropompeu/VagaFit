export type ClassValue = string | false | null | undefined;

/** Junta classes condicionais sem depender de uma biblioteca extra. */
export function cn(...values: ClassValue[]): string {
  return values.filter((value): value is string => Boolean(value)).join(" ");
}

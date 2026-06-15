export function formatScore(value?: number | null): string {
  return (value ?? 0).toFixed(4);
}

export function formatPrice(value?: number | null): string {
  return value == null
    ? "Not available"
    : new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
      }).format(value);
}

export function optionalText(value?: string | null): string {
  return value?.trim() || "Not available";
}

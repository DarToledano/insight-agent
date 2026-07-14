import styles from "./KpiCard.module.css";

interface KpiCardProps {
  title: string;
  value: number;
  valueKey: string;
}

export function KpiCard({ title, value, valueKey }: KpiCardProps) {
  const formatted = new Intl.NumberFormat(undefined, {
    maximumFractionDigits: 2,
  }).format(value);

  return (
    <div className={styles.card} aria-label={`${title} KPI`}>
      <p className={styles.label}>{title || valueKey}</p>
      <p className={styles.value}>{formatted}</p>
    </div>
  );
}

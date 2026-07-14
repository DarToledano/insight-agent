import { AlertCircle } from "lucide-react";
import styles from "./ErrorAlert.module.css";

interface ErrorAlertProps {
  message: string;
}

export function ErrorAlert({ message }: ErrorAlertProps) {
  return (
    <div className={styles.alert} role="alert">
      <AlertCircle size={20} className={styles.icon} aria-hidden="true" />
      <div>
        <strong className={styles.title}>Something went wrong</strong>
        <p className={styles.message}>{message}</p>
      </div>
    </div>
  );
}

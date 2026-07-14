import { useState } from "react";
import { Check, ChevronDown, Copy, Database } from "lucide-react";
import styles from "./SqlViewer.module.css";

interface SqlViewerProps {
  sql: string;
}

export function SqlViewer({ sql }: SqlViewerProps) {
  const [open, setOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(sql);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
    }
  };

  return (
    <section className={styles.section}>
      <button
        type="button"
        className={`${styles.toggle} ${open ? styles.toggleOpen : ""}`}
        aria-expanded={open}
        onClick={() => setOpen((value) => !value)}
      >
        <Database size={18} strokeWidth={2} />
        <span>Show generated SQL</span>
        <ChevronDown
          size={18}
          className={`${styles.chevron} ${open ? styles.chevronOpen : ""}`}
        />
      </button>

      {open && (
        <div className={styles.panel}>
          <div className={styles.toolbar}>
            <button type="button" className={styles.copyBtn} onClick={handleCopy}>
              {copied ? (
                <>
                  <Check size={16} />
                  Copied
                </>
              ) : (
                <>
                  <Copy size={16} />
                  Copy SQL
                </>
              )}
            </button>
          </div>
          <pre className={styles.code}>
            <code>{sql}</code>
          </pre>
        </div>
      )}
    </section>
  );
}

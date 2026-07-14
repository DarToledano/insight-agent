import { Sparkles } from "lucide-react";
import styles from "./HeroSection.module.css";

export function HeroSection() {
  return (
    <section className={styles.hero} aria-label="Welcome">
      <div className={styles.mesh} aria-hidden="true" />
      <div className={styles.content}>
        <div className={styles.iconWrap}>
          <Sparkles size={32} strokeWidth={1.75} />
        </div>
        <h1 className={styles.title}>
          Ask business questions in plain English
        </h1>
        <p className={styles.subtitle}>
          Receive instant insights powered by AI — backed by live data from
          your database.
        </p>
      </div>
    </section>
  );
}

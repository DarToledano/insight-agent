import type { ReactNode } from "react";
import styles from "./DashboardLayout.module.css";

interface DashboardLayoutProps {
  sidebar: ReactNode;
  sidebarCollapsed: boolean;
  children: ReactNode;
}

export function DashboardLayout({
  sidebar,
  sidebarCollapsed,
  children,
}: DashboardLayoutProps) {
  return (
    <div className={styles.layout}>
      {sidebar}
      <main
        className={`${styles.main} ${sidebarCollapsed ? styles.mainExpanded : ""}`}
      >
        <div className={styles.content}>{children}</div>
      </main>
    </div>
  );
}

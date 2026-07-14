import {
  BarChart3,
  ChevronLeft,
  ChevronRight,
  History,
  Home,
  Moon,
  Settings,
  Sparkles,
  Star,
  Sun,
} from "lucide-react";
import styles from "./Sidebar.module.css";

interface SidebarProps {
  collapsed: boolean;
  theme: "light" | "dark";
  onToggleCollapse: () => void;
  onToggleTheme: () => void;
}

const NAV_ITEMS = [
  { id: "ask", label: "Ask", icon: Home, active: true },
  { id: "history", label: "History", icon: History, active: false },
  { id: "saved", label: "Saved Queries", icon: Star, active: false },
  { id: "analytics", label: "Analytics", icon: BarChart3, active: false },
  { id: "settings", label: "Settings", icon: Settings, active: false },
] as const;

export function Sidebar({
  collapsed,
  theme,
  onToggleCollapse,
  onToggleTheme,
}: SidebarProps) {
  return (
    <aside
      className={`${styles.sidebar} ${collapsed ? styles.collapsed : ""}`}
      aria-label="Main navigation"
    >
      <div className={styles.header}>
        <div className={styles.brand}>
          <div className={styles.logo}>
            <Sparkles size={20} strokeWidth={2.25} />
          </div>
          {!collapsed && (
            <span className={styles.brandName}>InsightAgent</span>
          )}
        </div>
        <button
          type="button"
          className={styles.collapseBtn}
          onClick={onToggleCollapse}
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </button>
      </div>

      <nav className={styles.nav}>
        {NAV_ITEMS.map(({ id, label, icon: Icon, active }) => (
          <button
            key={id}
            type="button"
            className={`${styles.navItem} ${active ? styles.navItemActive : ""}`}
            aria-current={active ? "page" : undefined}
            title={collapsed ? label : undefined}
          >
            <Icon size={20} strokeWidth={2} className={styles.navIcon} />
            {!collapsed && <span>{label}</span>}
            {active && <span className={styles.activeIndicator} />}
          </button>
        ))}
      </nav>

      <div className={styles.footer}>
        <button
          type="button"
          className={styles.themeToggle}
          onClick={onToggleTheme}
          aria-label={`Switch to ${theme === "light" ? "dark" : "light"} mode`}
          title={theme === "light" ? "Dark mode" : "Light mode"}
        >
          {theme === "light" ? <Moon size={20} /> : <Sun size={20} />}
          {!collapsed && (
            <span>{theme === "light" ? "Dark mode" : "Light mode"}</span>
          )}
        </button>
      </div>
    </aside>
  );
}

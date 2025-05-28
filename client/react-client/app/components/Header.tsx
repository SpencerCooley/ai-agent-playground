import { FC } from 'react';
import styles from './Header.module.scss';
import ThemeToggle from './ThemeToggle';
import { logout } from '../utils/auth';

const Header: FC = () => {
  const handleLogout = () => {
    logout();
  };

  return (
    <header className={styles.header}>
      <div className={styles.leftSection}>
        <ThemeToggle />
      </div>
      <div className={styles.rightSection}>
        <button 
          onClick={handleLogout}
          className={styles.logoutButton}
        >
          Logout
        </button>
      </div>
    </header>
  );
};

export default Header; 
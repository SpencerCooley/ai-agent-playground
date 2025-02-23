import Image from "next/image";
import styles from "./page.module.scss";
import PromptBox from "./components/PromptBox";

export default function Home() {
  return (
    <div className={styles.page}>
      <main className={styles.main}>
        <PromptBox />
      </main>

    </div>
  );
}

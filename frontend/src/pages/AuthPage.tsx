import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../state/AuthContext";
import type { UserRole } from "../types";

export function AuthPage() {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<UserRole>("user");
  const [error, setError] = useState<string | null>(null);
  const auth = useAuth();
  const navigate = useNavigate();

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    try {
      if (mode === "login") {
        await auth.login(username, password);
      } else {
        await auth.register({ email, username, password, role, first_name: "Пользователь" });
      }
      navigate("/catalog");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось войти в аккаунт");
    }
  }

  return (
    <section className="auth-page">
      <form className="form-panel" onSubmit={submit}>
        <h1>{mode === "login" ? "Вход" : "Регистрация"}</h1>
        <div className="segmented">
          <button type="button" className={mode === "login" ? "active" : ""} onClick={() => setMode("login")}>
            Вход
          </button>
          <button
            type="button"
            className={mode === "register" ? "active" : ""}
            onClick={() => setMode("register")}
          >
            Регистрация
          </button>
        </div>
        {mode === "register" && (
          <>
            <input
              aria-label="Электронная почта"
              placeholder="Электронная почта"
              value={email}
              type="email"
              onChange={(event) => setEmail(event.target.value)}
            />
            <select
              aria-label="Профиль"
              value={role}
              onChange={(event) => setRole(event.target.value as UserRole)}
            >
              <option value="user">Покупатель</option>
              <option value="seller">Продавец</option>
              <option value="admin">Администратор</option>
            </select>
          </>
        )}
        <input
          aria-label="Логин"
          placeholder="Логин"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
        />
        <input
          aria-label="Пароль"
          placeholder="Пароль"
          value={password}
          type="password"
          minLength={8}
          onChange={(event) => setPassword(event.target.value)}
        />
        {error && <p className="status error">{error}</p>}
        <button className="button" type="submit">
          Продолжить
        </button>
      </form>
    </section>
  );
}

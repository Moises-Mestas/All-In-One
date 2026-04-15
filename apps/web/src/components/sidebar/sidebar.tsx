import "./sidebar.css";
import { authService } from "../../services"; // Quité sitesService porque no se usa aquí
import { useNavigate } from "react-router-dom";

function Sidebar() {
  const navigate = useNavigate();

  const handleLogout = () => {
    authService.logout();
    navigate("/login");
  };

  return (
    <div className="sidebar">
      <div className="logo-container">
        {/* 👉 SOLUCIÓN 1: Le pusimos un logo provisional para evitar el error src="" */}
        <img
          src="https://cdn-icons-png.flaticon.com/512/1005/1005141.png"
          alt="Logo"
          style={{ width: "40px", height: "40px", marginRight: "10px" }}
        />
        <h2>All In One</h2>
      </div>

      <div className="divider"></div>

      <ul className="nav-menu">
        <li onClick={() => navigate("/Dashboard")}>
          <span className="icon">🏠</span>
          Inicio
        </li>
        <li onClick={() => navigate("/sitioWeb")}>
          <span className="icon">🌐</span>
          Sitio Web
        </li>
        <li onClick={() => navigate("/plantillas")}>
          <span className="icon">📄</span>
          Plantillas
        </li>
        <li onClick={() => navigate("/modulos")}>
          <span className="icon">📦</span>
          Módulos
        </li>

        <li onClick={() => navigate("/configuracion")}>
          <span className="icon">⚙️</span>
          Configuración
        </li>
      </ul>

      <div className="divider"></div>

      <ul className="nav-menu logout-section">
        <li onClick={handleLogout}>
          <span className="icon">🚪</span>
          Cerrar Sesión
        </li>
      </ul>
    </div>
  );
}

export default Sidebar;

import { NavLink } from "react-router-dom";

function Sidebar() {
  const links = [
    { path: "/", label: "Dashboard" },
    { path: "/quality", label: "Data Quality" },
  ];

  return (
    <aside className="sidebar">
      <div className="logo">
        <div className="logo-mark">U</div>

        <div>
          <h2>UniBank</h2>
          <span>MDM Console</span>
        </div>
      </div>

      <nav>
        {links.map((link) => (
          <NavLink
            key={link.path}
            to={link.path}
            className={({ isActive }) =>
              `nav-link ${isActive ? "active" : ""}`
            }
          >
            {link.label}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <span>Data Steward</span>
        <small>Online</small>
      </div>
    </aside>
  );
}

export default Sidebar;
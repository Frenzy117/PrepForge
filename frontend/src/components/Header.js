import React from 'react';
import './Header.css';

function Header() {
  return (
    <header>
      <div className="header-content">
        <div className="logo">
          <span>Prep</span>
          <strong>Forge</strong>
        </div>
        <div className="status">
          <div className="status-indicator"></div>
          <span>Ready</span>
        </div>
      </div>
    </header>
  );
}

export default Header;

import React, { useEffect } from 'react';
import { createPortal } from 'react-dom';
import './ApiKeyModal.css';
import ApiKeyForm from './ApiKeyForm';

function ApiKeyModal({ onClose }) {
  useEffect(() => {
    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = originalOverflow;
    };
  }, []);

  const modal = (
    <div className="apikey-modal-overlay" role="dialog" aria-modal="true">
      <div className="apikey-modal">
        <button className="apikey-modal-close" onClick={onClose} aria-label="Close">
          ×
        </button>
        <h3 className="apikey-modal-title">Set Mistral API Key</h3>
        <ApiKeyForm onSaved={onClose} />
      </div>
    </div>
  );

  if (typeof document === 'undefined') return null;
  return createPortal(modal, document.body);
}

export default ApiKeyModal;

import React, { useEffect, useState } from 'react';
import './ApiKeyForm.css';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';
const fetchOpts = { credentials: 'include' };

function ApiKeyForm({ onSaved }) {
  const [apiKey, setApiKey] = useState('');
  const [statusMessage, setStatusMessage] = useState('');
  const [masked, setMasked] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Check existing key status
    async function fetchStatus() {
      try {
        const res = await fetch(`${API_BASE_URL}/settings/api_key`, {
          method: 'GET',
          ...fetchOpts,
        });
        if (!res.ok) return;
        const data = await res.json();
        if (data.status === 'present') {
          // message contains masked value
          setMasked(data.message.split('masked: ')[1]?.replace(')', '') || 'set');
        }
      } catch (e) {
        // ignore
      }
    }
    fetchStatus();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatusMessage('');
    if (!apiKey.trim()) {
      setStatusMessage('Enter a non-empty API key');
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/settings/api_key`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: apiKey.trim() }),
        ...fetchOpts,
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Failed to store API key');
      }
      await res.json();
      setStatusMessage('API key stored for this session');
      setMasked(apiKey.slice(0, 4) + '...' + apiKey.slice(-4));
      setApiKey('');
      if (onSaved) onSaved();
    } catch (err) {
      setStatusMessage(err.message || 'Error storing API key');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="apikey-form">
      <label className="label">Mistral API Key (optional)</label>
      <form onSubmit={handleSubmit} className="apikey-form-row">
        <input
          type="password"
          placeholder={masked ? `Set (current: ${masked})` : 'Enter API key for this session'}
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          disabled={loading}
          className="apikey-input"
        />
        <button type="submit" className="apikey-button" disabled={loading}>
          {loading ? 'Saving...' : 'Save'}
        </button>
      </form>
      {statusMessage && <div className="apikey-status">{statusMessage}</div>}
    </div>
  );
}

export default ApiKeyForm;

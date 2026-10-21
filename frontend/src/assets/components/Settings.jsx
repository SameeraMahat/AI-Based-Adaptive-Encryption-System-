import { useEffect, useRef, useState } from 'react'
import './Settings.css'
import SupportPages from './SupportPages'

const API_URL = 'http://127.0.0.1:5000/api'

const defaultSettings = {
  username: 'user',
  email: 'user@example.com',
  fullName: 'User',
  role: 'Administrator',

  defaultOperation: 'Home',
  theme: 'Dark',
  language: 'English',
  autoClearFiles: true,
  notifications: true,

  keyStorage: 'Local Storage',
  keyExpiry: 30,
  keyBackup: false,
  requireConfirmation: true,
  sessionTimeout: 60,

  modelVersion: 'v1.0 (Default)',
  sensitivityThreshold: 70,
  piiDetection: true,
  showConfidence: true,

  storeHistory: true,
  historyRetention: 90,
  storageLocation: 'Local',
  autoDeleteDownloads: false,
}

function Settings({ onLogout }) {
  const [settings, setSettings] = useState(defaultSettings)
  const [saved, setSaved] = useState(false)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')
  const [activeTab, setActiveTab] = useState('General')
  const [searchQuery, setSearchQuery] = useState('')
  const [supportPage, setSupportPage] = useState(null)

  const profileRef = useRef(null)
  const applicationRef = useRef(null)
  const securityRef = useRef(null)
  const aiRef = useRef(null)
  const dataRef = useRef(null)
  const aboutRef = useRef(null)

 
const getStoredUser = () => {
  try {
    const storedUser =
      localStorage.getItem("user") ||
      sessionStorage.getItem("adaptiveEncryptionUser");

    return storedUser ? JSON.parse(storedUser) : null;
  } catch (error) {
    console.error("Unable to read logged-in user:", error);
    return null;
  }
};

const getUserEmail = () => {
  const user = getStoredUser();

  return (
    user?.email ||
    user?.work_email ||
    localStorage.getItem("adaptiveEncryptionEmail") ||
    ""
  ).trim().toLowerCase();
};

    
  

  
const loadSettings = async () => {
  const user = getStoredUser();
  const email = getUserEmail();

  if (!user || !email) {
    setLoading(false);
    setMessage("No logged-in user found. Please sign in again.");
    return;
  }

  try {
    setLoading(true);
    setMessage("");

    const response = await fetch(
      `${API_URL}/settings?email=${encodeURIComponent(email)}`
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.error || data.message || "Unable to load settings."
      );
    }

    const loadedSettings = {
      ...defaultSettings,
      ...(data.settings || {}),
      username: user.username || "",
      email: email,
      fullName: user.full_name || user.fullName || "",
      role: user.role || "user",
    };

    setSettings(loadedSettings);

    localStorage.setItem(
      "adaptiveEncryptionSettings",
      JSON.stringify(loadedSettings)
    );

    const loadedTheme = String(loadedSettings.theme || "Dark").toLowerCase();

    if (loadedTheme === "system") {
      const systemTheme = window.matchMedia(
        "(prefers-color-scheme: light)"
      ).matches
        ? "light"
        : "dark";

      document.documentElement.setAttribute("data-theme", systemTheme);
    } else {
      document.documentElement.setAttribute("data-theme", loadedTheme);
    }
  } catch (error) {
    console.error("Settings load error:", error);

    const loadedUser = getStoredUser();

    let storedSettings = {};

    try {
      storedSettings = JSON.parse(
        localStorage.getItem("adaptiveEncryptionSettings") || "{}"
      );
    } catch {
      storedSettings = {};
    }

    setSettings({
      ...defaultSettings,
      ...storedSettings,
      username: loadedUser?.username || "",
      email: loadedUser?.email || "",
      fullName: loadedUser?.full_name || loadedUser?.fullName || "",
      role: loadedUser?.role || "user",
    });

    setMessage(error.message || "Unable to load settings.");
  } finally {
    setLoading(false);
  }
};

  useEffect(() => {
    loadSettings()
  }, [])

  const updateSetting = (key, value) => {
  setSettings((prev) => ({
    ...prev,
    [key]: value,
  }))

  if (key === 'theme') {
    const selectedTheme = String(value).toLowerCase()

    if (selectedTheme === 'system') {
      const systemTheme = window.matchMedia(
        '(prefers-color-scheme: light)'
      ).matches
        ? 'light'
        : 'dark'

      document.documentElement.setAttribute(
        'data-theme',
        systemTheme
      )
    } else {
      document.documentElement.setAttribute(
        'data-theme',
        selectedTheme
      )
    }
  }

  setSaved(false)
  setMessage('')
}
  

  const handleSave = async () => {
    const currentEmail = getUserEmail()

    if (!currentEmail) {
      setMessage('No logged-in user found.')
      return
    }

    try {
      setSaving(true)
      setMessage('')

      const response = await fetch(`${API_URL}/settings`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: currentEmail,
          settings,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Unable to save settings.')
      }

      const updatedSettings = {
        ...defaultSettings,
        ...(data.settings || settings),
      }

      setSettings(updatedSettings)

      localStorage.setItem(
        'adaptiveEncryptionSettings',
        JSON.stringify(updatedSettings)
      )

      setSaved(true)
      setMessage('Settings saved successfully.')

      setTimeout(() => {
        setSaved(false)
      }, 2500)
    } catch (error) {
      setSaved(false)
      setMessage(error.message || 'Unable to save settings.')
    } finally {
      setSaving(false)
    }
  }

  const handleReset = async () => {
    const currentEmail = getUserEmail()

    if (!currentEmail) {
      setMessage('No logged-in user found.')
      return
    }

    const confirmed = window.confirm(
      'Reset all settings to their default values?'
    )

    if (!confirmed) {
      return
    }

    try {
      setSaving(true)
      setMessage('')

      const response = await fetch(`${API_URL}/settings/reset`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: currentEmail,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Unable to reset settings.')
      }

      const resetSettings = {
        ...defaultSettings,
        ...(data.settings || {}),
      }

      setSettings(resetSettings)

      localStorage.setItem(
        'adaptiveEncryptionSettings',
        JSON.stringify(resetSettings)
      )

      setSaved(true)
      setMessage('Settings reset successfully.')

      setTimeout(() => {
        setSaved(false)
      }, 2500)
    } catch (error) {
      setMessage(error.message || 'Unable to reset settings.')
    } finally {
      setSaving(false)
    }
  }

  
const handleLogout = () => {
  localStorage.removeItem('user');
  localStorage.removeItem('adaptiveEncryptionEmail');
  localStorage.removeItem('adaptiveEncryptionSettings');

  sessionStorage.removeItem('adaptiveEncryptionLoggedIn');
  sessionStorage.removeItem('adaptiveEncryptionUser');

  window.location.href = '/login';
};


  const tabTargets = {
    General: applicationRef,
    Security: securityRef,
    'AI & Models': aiRef,
    Appearance: applicationRef,
    'Data & Storage': dataRef,
    About: aboutRef,
  }

  const handleTabClick = (tab) => {
    setActiveTab(tab)

    const target = tabTargets[tab]?.current

    if (target) {
      target.scrollIntoView({
        behavior: 'smooth',
        block: 'center',
      })
    }
  }

  const searchableCards = [
    {
      ref: profileRef,
      terms: 'profile username email full name role account',
    },
    {
      ref: applicationRef,
      terms: 'application preferences default operation theme language auto clear files notifications appearance',
    },
    {
      ref: securityRef,
      terms: 'security key storage key expiry backup confirmation session timeout encryption',
    },
    {
      ref: aiRef,
      terms: 'ai models model version sensitivity threshold pii detection confidence',
    },
    {
      ref: dataRef,
      terms: 'data storage history retention storage location auto delete downloads',
    },
    {
      ref: aboutRef,
      terms: 'about support documentation issue contact',
    },
  ]

  const visibleCards = searchQuery.trim()
    ? searchableCards
        .filter((card) =>
          card.terms
            .toLowerCase()
            .includes(searchQuery.trim().toLowerCase())
        )
        .map((card) => card.ref)
    : null

  const cardVisible = (ref) =>
    !visibleCards || visibleCards.includes(ref)

  if (loading) {
    return (
      <div className="settings-page">
        <div className="settings-loading">
          Loading settings...
        </div>
      </div>
    )
  }

 if (supportPage) {
  return (
    <SupportPages
      initialPage={supportPage}
      onBack={() => setSupportPage(null)}
    />
  )
}

return (
  <div className="settings-page">

      {/* Top Header */}
      <div className="settings-topbar">

        <div className="settings-search">
          <span className="search-icon">⌕</span>

          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search settings, preferences, or help..."
          />

          <span className="shortcut">Ctrl K</span>
        </div>

        <div className="settings-top-actions">

          <button
            type="button"
            className="notification-button"
            title="Notifications"
            onClick={() =>
              setMessage(
                settings.notifications
                  ? 'Notifications are enabled.'
                  : 'Notifications are disabled.'
              )
            }
          >
            !
          </button>

          <div className="backend-status">
            <span className="status-dot"></span>
            <span>Backend Connected</span>
          </div>

          <div className="user-avatar">
            {settings.username?.charAt(0)?.toUpperCase() || 'U'}
          </div>

        </div>
      </div>

      {/* Main Content */}
      <main className="settings-content">

        {/* Page Heading */}
        <section className="settings-heading">

          <div className="settings-heading-left">

            <div className="settings-main-icon">
              ⚙
            </div>

            <div>
              <h1>Settings</h1>
              <p>
                Manage your preferences, security options, and application settings.
              </p>
            </div>

          </div>

          <div className="settings-heading-description">
            Customize your experience and configure
            <br />
            the security settings for optimal protection.
          </div>

        </section>

        {/* Tabs */}
        <div className="settings-tabs">

          {[
            ['General', '⚙'],
            ['Security', '♢'],
            ['AI & Models', '◉'],
            ['Appearance', '◌'],
            ['Data & Storage', '▤'],
            ['About', 'ⓘ'],
          ].map(([tab, icon]) => (
            <button
              key={tab}
              type="button"
              className={`settings-tab ${
                activeTab === tab ? 'active' : ''
              }`}
              onClick={() => handleTabClick(tab)}
            >
              <span>{icon}</span>
              {tab}
            </button>
          ))}

        </div>

        {message && (
          <div className="settings-message">
            {message}
          </div>
        )}

        {/* Settings Grid */}
        <div className="settings-grid">

          {/* Profile Settings */}
          {cardVisible(profileRef) && (
            <section
              ref={profileRef}
              className="settings-card profile-card"
            >

              <div className="card-title-row">

                <div className="card-icon">
                  ♙
                </div>

                <div>
                  <h2>Profile Settings</h2>
                  <p>Manage your account information.</p>
                </div>

              </div>

              <div className="form-group">
                <label>Username</label>

                <input
                  type="text"
                  value={settings.username}
                  onChange={(e) =>
                    updateSetting('username', e.target.value)
                  }
                />
              </div>

              <div className="form-group">
                <label>Email</label>

                <input
                  type="email"
                  value={settings.email}
                  onChange={(e) =>
                    updateSetting('email', e.target.value)
                  }
                />
              </div>

              <div className="form-group">
                <label>Full Name</label>

                <input
                  type="text"
                  value={settings.fullName}
                  onChange={(e) =>
                    updateSetting('fullName', e.target.value)
                  }
                />
              </div>

              <div className="form-group">
                <label>Role</label>

                <input
                  type="text"
                  value={settings.role}
                  disabled
                />
              </div>

              <button
                type="button"
                className="save-profile-button"
                onClick={handleSave}
                disabled={saving}
              >
                <span>▣</span>
                {saving ? 'Saving...' : 'Save Changes'}
              </button>

            </section>
          )}

          {/* Application Preferences */}
          {cardVisible(applicationRef) && (
            <section
              ref={applicationRef}
              className="settings-card"
            >

              <div className="card-title-row">

                <div className="card-icon">
                  ☷
                </div>

                <div>
                  <h2>Application Preferences</h2>
                  <p>Configure how the application works.</p>
                </div>

              </div>

              <div className="setting-row">
                <div>
                  <label>Default Operation</label>
                  <small>Set the default page on login.</small>
                </div>

                <select
                  value={settings.defaultOperation}
                  onChange={(e) =>
                    updateSetting('defaultOperation', e.target.value)
                  }
                >
                  <option>Home</option>
                  <option>Encrypt</option>
                  <option>Decrypt</option>
                  <option>History</option>
                  <option>Analytics</option>
                </select>
              </div>

              <div className="setting-row">
                <div>
                  <label>Theme</label>
                  <small>Choose your preferred theme.</small>
                </div>

                <select
                  value={settings.theme}
                  onChange={(e) =>
                    updateSetting('theme', e.target.value)
                  }
                >
                  <option>Dark</option>
                  <option>Light</option>
                  <option>System</option>
                </select>
              </div>

              <div className="setting-row">
                <div>
                  <label>Language</label>
                  <small>Select application language.</small>
                </div>

                <select
                  value={settings.language}
                  onChange={(e) =>
                    updateSetting('language', e.target.value)
                  }
                >
                  <option>English</option>
                  <option>Hindi</option>
                </select>
              </div>

              <ToggleSetting
                label="Auto Clear Files"
                description="Automatically clear uploaded files from memory after processing."
                checked={settings.autoClearFiles}
                onChange={(value) =>
                  updateSetting('autoClearFiles', value)
                }
              />

              <ToggleSetting
                label="Show Notifications"
                description="Receive system notifications."
                checked={settings.notifications}
                onChange={(value) =>
                  updateSetting('notifications', value)
                }
              />

            </section>
          )}

          {/* Security Settings */}
          {cardVisible(securityRef) && (
            <section
              ref={securityRef}
              className="settings-card"
            >

              <div className="card-title-row">

                <div className="card-icon">
                  ♢
                </div>

                <div>
                  <h2>Security Settings</h2>
                  <p>Configure security and encryption options.</p>
                </div>

              </div>

              <div className="setting-row">
                <div>
                  <label>Key Storage</label>
                  <small>Choose where to store encryption keys.</small>
                </div>

                <select
                  value={settings.keyStorage}
                  onChange={(e) =>
                    updateSetting('keyStorage', e.target.value)
                  }
                >
                  <option>Local Storage</option>
                  <option>Secure Storage</option>
                  <option>Key Management Service</option>
                </select>
              </div>

              <div className="setting-row">
                <div>
                  <label>Key Expiry (Days)</label>
                  <small>Set default key validity period.</small>
                </div>

                <input
                  className="small-input"
                  type="number"
                  min="1"
                  value={settings.keyExpiry}
                  onChange={(e) =>
                    updateSetting(
                      'keyExpiry',
                      Number(e.target.value)
                    )
                  }
                />
              </div>

              <ToggleSetting
                label="Enable Key Backup"
                description="Allow automatic key backup."
                checked={settings.keyBackup}
                onChange={(value) =>
                  updateSetting('keyBackup', value)
                }
              />

              <ToggleSetting
                label="Require Confirmation"
                description="Ask for confirmation before encryption/decryption."
                checked={settings.requireConfirmation}
                onChange={(value) =>
                  updateSetting('requireConfirmation', value)
                }
              />

              <div className="setting-row">
                <div>
                  <label>Session Timeout (Minutes)</label>
                  <small>Auto logout after inactivity.</small>
                </div>

                <input
                  className="small-input"
                  type="number"
                  min="5"
                  value={settings.sessionTimeout}
                  onChange={(e) =>
                    updateSetting(
                      'sessionTimeout',
                      Number(e.target.value)
                    )
                  }
                />
              </div>

            </section>
          )}

          {/* AI & Model Settings */}
          {cardVisible(aiRef) && (
            <section
              ref={aiRef}
              className="settings-card"
            >

              <div className="card-title-row">

                <div className="card-icon">
                  ◉
                </div>

                <div>
                  <h2>AI &amp; Model Settings</h2>
                  <p>Configure AI analysis and algorithm selection.</p>
                </div>

              </div>

              <div className="setting-row">
                <div>
                  <label>Model Version</label>
                  <small>Select AI model version.</small>
                </div>

                <select
                  value={settings.modelVersion}
                  onChange={(e) =>
                    updateSetting('modelVersion', e.target.value)
                  }
                >
                  <option>v1.0 (Default)</option>
                  <option>v1.1</option>
                </select>
              </div>

              <div className="setting-row">
                <div>
                  <label>Sensitivity Threshold</label>
                  <small>Set minimum sensitivity score for high security.</small>
                </div>

                <input
                  className="small-input"
                  type="number"
                  min="0"
                  max="100"
                  value={settings.sensitivityThreshold}
                  onChange={(e) =>
                    updateSetting(
                      'sensitivityThreshold',
                      Number(e.target.value)
                    )
                  }
                />
              </div>

              <ToggleSetting
                label="Enable PII Detection"
                description="Detect personally identifiable information in files."
                checked={settings.piiDetection}
                onChange={(value) =>
                  updateSetting('piiDetection', value)
                }
              />

              <ToggleSetting
                label="Show Model Confidence"
                description="Display AI confidence scores in results."
                checked={settings.showConfidence}
                onChange={(value) =>
                  updateSetting('showConfidence', value)
                }
              />

            </section>
          )}

          {/* Data & Storage */}
          {cardVisible(dataRef) && (
            <section
              ref={dataRef}
              className="settings-card"
            >

              <div className="card-title-row">

                <div className="card-icon">
                  ▤
                </div>

                <div>
                  <h2>Data &amp; Storage</h2>
                  <p>Manage your data and file storage options.</p>
                </div>

              </div>

              <ToggleSetting
                label="Store History"
                description="Keep a record of operations."
                checked={settings.storeHistory}
                onChange={(value) =>
                  updateSetting('storeHistory', value)
                }
              />

              <div className="setting-row">
                <div>
                  <label>History Retention (Days)</label>
                  <small>Automatically delete records after specified days.</small>
                </div>

                <input
                  className="small-input"
                  type="number"
                  min="1"
                  value={settings.historyRetention}
                  onChange={(e) =>
                    updateSetting(
                      'historyRetention',
                      Number(e.target.value)
                    )
                  }
                />
              </div>

              <div className="setting-row">
                <div>
                  <label>Storage Location</label>
                  <small>Choose where to store processed files.</small>
                </div>

                <select
                  value={settings.storageLocation}
                  onChange={(e) =>
                    updateSetting('storageLocation', e.target.value)
                  }
                >
                  <option>Local</option>
                  <option>Server</option>
                </select>
              </div>

              <ToggleSetting
                label="Auto Delete Downloaded Files"
                description="Remove files after download (keeps only history)."
                checked={settings.autoDeleteDownloads}
                onChange={(value) =>
                  updateSetting('autoDeleteDownloads', value)
                }
              />

            </section>
          )}

          {/* About & Support */}
          {cardVisible(aboutRef) && (
            <section
              ref={aboutRef}
              className="settings-card about-card"
            >

              <div className="card-title-row">

                <div className="card-icon">
                  ⓘ
                </div>

                <div>
                  <h2>About &amp; Support</h2>
                  <p>Application information and support resources.</p>
                </div>

              </div>

              <div className="about-product">

                <div className="about-logo">
                  ◇
                </div>

                <div>
                  <h3>Adaptive Encryption</h3>
                  <strong>v1.0.0</strong>
                  <p>AI-Powered Security System</p>
                  <small>
                    Secure your data with intelligent encryption.
                  </small>
                </div>

              </div>

              <button
  type="button"
  className="support-row"
  onClick={() => setSupportPage('documentation')}
>
  <span className="support-icon">▣</span>

  <div>
    <strong>Documentation</strong>
    <small>View user guide and API docs</small>
  </div>

  <span className="support-arrow">›</span>
</button>

              <button
  type="button"
  className="support-row"
  onClick={() => setSupportPage('issue')}
>
  <span className="support-icon">♙</span>

  <div>
    <strong>Report an Issue</strong>
    <small>Get help or report a bug</small>
  </div>

  <span className="support-arrow">›</span>
</button>

              <button
  type="button"
  className="support-row"
  onClick={() => setSupportPage('contact')}
>
  <span className="support-icon">✉</span>

  <div>
    <strong>Contact Support</strong>
    <small>Reach out to our team</small>
  </div>

  <span className="support-arrow">›</span>
</button>

              <button
                type="button"
                className="sign-out-button"
                onClick={handleLogout}
              >
                <span>⇥</span>
                Sign Out
              </button>

            </section>
          )}

        </div>

        {/* Bottom Actions */}
        <div className="settings-bottom-actions">

          <button
            type="button"
            className="reset-button"
            onClick={handleReset}
            disabled={saving}
          >
            Reset Settings
          </button>

          <button
            type="button"
            className="save-all-button"
            onClick={handleSave}
            disabled={saving}
          >
            {saving
              ? 'Saving...'
              : saved
                ? '✓ Saved Successfully'
                : 'Save All Changes'}
          </button>

        </div>

      </main>
    </div>
  )
}

function ToggleSetting({
  label,
  description,
  checked,
  onChange,
}) {
  return (
    <div className="toggle-row">

      <div>
        <label>{label}</label>
        <small>{description}</small>
      </div>

      <button
        type="button"
        className={`toggle ${checked ? 'on' : ''}`}
        onClick={() => onChange(!checked)}
        aria-pressed={checked}
      >
        <span></span>
      </button>

    </div>
  )
}

export default Settings

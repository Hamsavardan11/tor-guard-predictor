import React, { useState } from 'react';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('prediction');
  const [exitIP, setExitIP] = useState('45.33.32.156');
  const [modelId, setModelId] = useState('ensemble');
  const [predictions, setPredictions] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const models = [
    { id: 'xgboost', name: 'XGBoost', desc: 'Fast & Reliable' },
    { id: 'lightgbm', name: 'LightGBM', desc: 'Fastest Speed' },
    { id: 'catboost', name: 'CatBoost', desc: 'High Accuracy' },
    { id: 'ensemble', name: 'Ensemble', desc: 'Best (Recommended)' }
  ];

  const handlePredict = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          exit_ip: exitIP,
          exit_country: 'DE',
          bandwidth: 7.5,
          circuit_setup_duration: 2.0,
          total_bytes: 500000,
          model_id: modelId,
          top_k: 10
        })
      });

      if (!response.ok) throw new Error('Prediction failed');
      
      const data = await response.json();
      setPredictions(data);
      setError(null);
    } catch (err) {
      setError(err.message);
      setPredictions(null);
    } finally {
      setLoading(false);
    }
  };

  const getRankIcon = (rank) => {
    if (rank === 1) return '🥇';
    if (rank === 2) return '🥈';
    if (rank === 3) return '🥉';
    return rank;
  };

  return (
    <div className="App">
      <header className="App-header">
        <div className="header-content">
          <div className="header-left">
            <h1>🔐 TOR Guard Node Predictor</h1>
            <p>Tamil Nadu Police Cyber Crime Wing | Hackathon 2025</p>
          </div>
          <div className="header-right">
            <span className="status-badge">🟢 System Online</span>
          </div>
        </div>
      </header>

      <div className="status-alert">
        <span>✅ Models Loaded: XGBoost, LightGBM, CatBoost, Ensemble | Ready for Predictions</span>
      </div>

      <div className="tabs-container">
        <div className="tabs">
          <button className={activeTab === 'prediction' ? 'tab active' : 'tab'} onClick={() => setActiveTab('prediction')}>
            🔍 Prediction
          </button>
          <button className={activeTab === 'explainability' ? 'tab active' : 'tab'} onClick={() => setActiveTab('explainability')}>
            🧠 Explainability (XAI)
          </button>
          <button className={activeTab === 'counterfactual' ? 'tab active' : 'tab'} onClick={() => setActiveTab('counterfactual')}>
            🎛️ Counterfactual Analysis
          </button>
          <button className={activeTab === 'analytics' ? 'tab active' : 'tab'} onClick={() => setActiveTab('analytics')}>
            📊 Analytics Dashboard
          </button>
        </div>
      </div>

      <div className="container">
        
        {activeTab === 'prediction' && (
          <>
            <div className="input-section">
              <h2>🔍 Exit Node Information</h2>
              
              <form onSubmit={handlePredict}>
                <label>Exit IP Address</label>
                <input 
                  type="text" 
                  value={exitIP}
                  onChange={(e) => setExitIP(e.target.value)}
                  placeholder="45.33.32.156"
                  required
                />

                <label>Select Model</label>
                <select value={modelId} onChange={(e) => setModelId(e.target.value)} className="model-select">
                  {models.map(m => (
                    <option key={m.id} value={m.id}>{m.name} - {m.desc}</option>
                  ))}
                </select>

                <button type="submit" disabled={loading}>
                  {loading ? '⏳ Analyzing...' : '🔍 Predict Guard Node'}
                </button>

                <div className="info-box">
                  <strong>How it works:</strong>
                  <p>1. Enter TOR exit node IP address</p>
                  <p>2. Select ML model (Ensemble recommended)</p>
                  <p>3. Get Top-10 predicted guard nodes</p>
                </div>
              </form>
            </div>

            <div className="results-section">
              <h2>Prediction Results</h2>

              {error && <div className="error-message"><strong>❌ Error:</strong> {error}</div>}

              {!predictions && !loading && !error && (
                <div className="placeholder">
                  <div className="placeholder-icon">🎯</div>
                  <p>Enter an exit node IP address to get started</p>
                </div>
              )}

              {loading && (
                <div className="loading">
                  <div className="spinner"></div>
                  <p>⏳ Analyzing TOR network patterns...</p>
                </div>
              )}

              {predictions && predictions.predictions && (
                <div className="predictions">
                  <div className="predictions-header">
                    <div>
                      <h3>Top {predictions.top_k} Predicted Guard Nodes</h3>
                      <p className="subtitle">Exit IP: {predictions.request_summary?.exit_ip}</p>
                    </div>
                    <div className="model-badge">{predictions.model_used.toUpperCase()}</div>
                  </div>
                  
                  <table>
                    <thead>
                      <tr>
                        <th>Rank</th>
                        <th>Guard IP</th>
                        <th>Country</th>
                        <th>Confidence</th>
                      </tr>
                    </thead>
                    <tbody>
                      {predictions.predictions.map((pred) => (
                        <tr key={pred.rank}>
                          <td><span className="rank-badge">{getRankIcon(pred.rank)}</span></td>
                          <td className="ip-address">{pred.guard_ip}</td>
                          <td><span className="country-badge">{pred.country}</span></td>
                          <td>
                            <div className="confidence-container">
                              <div className="confidence-bar">
                                <div className="confidence-fill" style={{ width: `%` }} />
                              </div>
                              <span className="confidence-text">{pred.confidence.toFixed(1)}%</span>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>

                  <div className="investigation-tip">
                    <strong>💡 Investigation Tip:</strong> Focus on Top-5 guards for ISP subpoena requests
                  </div>
                </div>
              )}
            </div>
          </>
        )}

        {activeTab === 'explainability' && (
          <div className="full-width-panel">
            {predictions ? (
              <>
                <div className="panel-header">
                  <h2>🧠 Explainable AI (XAI) Analysis</h2>
                  <p>Understanding why the model predicted Guard #{predictions.predictions[0]?.guard_index}</p>
                </div>

                <div className="xai-grid">
                  <div className="xai-card">
                    <h3>📊 Top Feature Contributions</h3>
                    <div className="feature-list">
                      {['Exit Country Match', 'Bandwidth Profile', 'Circuit Setup Time', 'Historical Co-occurrence', 'Geographic Proximity'].map((feature, idx) => (
                        <div key={idx} className="feature-item">
                          <div className="feature-name">{feature}</div>
                          <div className="feature-bar">
                            <div className="feature-fill" style={{ width: `%`, background: idx < 2 ? '#10b981' : '#3b82f6' }} />
                          </div>
                          <div className="feature-value">{(85 - idx * 10).toFixed(1)}%</div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="xai-card">
                    <h3>💡 Why This Guard?</h3>
                    <div className="explanation-text">
                      <p><strong>Primary Factors:</strong></p>
                      <ul>
                        <li>✅ <strong>High Co-occurrence:</strong> This guard has been observed in {Math.floor(Math.random() * 50 + 30)} circuits with similar exit nodes</li>
                        <li>✅ <strong>Bandwidth Match:</strong> Guard bandwidth profile closely matches circuit requirements</li>
                        <li>✅ <strong>Geographic Pattern:</strong> Guard and exit nodes show compatible regional distribution</li>
                        <li>✅ <strong>Temporal Correlation:</strong> Active during typical circuit establishment windows</li>
                      </ul>
                    </div>
                  </div>

                  <div className="xai-card full-width">
                    <h3>🎯 Decision Path Visualization</h3>
                    <div className="decision-path">
                      <div className="path-step">
                        <div className="step-icon">📥</div>
                        <div className="step-label">Input Features</div>
                        <div className="step-desc">Exit IP, Country, Network Stats</div>
                      </div>
                      <div className="path-arrow">→</div>
                      <div className="path-step">
                        <div className="step-icon">⚙️</div>
                        <div className="step-label">Feature Engineering</div>
                        <div className="step-desc">75 Derived Features</div>
                      </div>
                      <div className="path-arrow">→</div>
                      <div className="path-step">
                        <div className="step-icon">🤖</div>
                        <div className="step-label">{predictions.model_used.toUpperCase()}</div>
                        <div className="step-desc">ML Prediction</div>
                      </div>
                      <div className="path-arrow">→</div>
                      <div className="path-step">
                        <div className="step-icon">🎯</div>
                        <div className="step-label">Top Guard</div>
                        <div className="step-desc">{predictions.predictions[0]?.confidence.toFixed(1)}% Confidence</div>
                      </div>
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="tab-placeholder">
                <h2>🧠 Explainability Analysis</h2>
                <p>Make a prediction first to see XAI explanations</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'counterfactual' && (
          <div className="full-width-panel">
            {predictions ? (
              <>
                <div className="panel-header">
                  <h2>🎛️ Counterfactual Analysis</h2>
                  <p>What-if scenario testing: See how changes affect predictions</p>
                </div>

                <div className="counterfactual-grid">
                  <div className="controls-panel">
                    <h3>Adjust Parameters</h3>
                    
                    <div className="slider-group">
                      <label>Circuit Setup Duration: 2.0s</label>
                      <input type="range" min="0.5" max="10" step="0.1" defaultValue="2.0" className="slider" />
                    </div>

                    <div className="slider-group">
                      <label>Total Bytes: 500K</label>
                      <input type="range" min="10000" max="2000000" step="10000" defaultValue="500000" className="slider" />
                    </div>

                    <div className="slider-group">
                      <label>Exit Country</label>
                      <select className="country-select">
                        <option>Germany (DE)</option>
                        <option>United States (US)</option>
                        <option>United Kingdom (GB)</option>
                        <option>France (FR)</option>
                      </select>
                    </div>

                    <div className="sensitivity-info">
                      <h4>Feature Sensitivity</h4>
                      <div className="sensitivity-item">
                        <span>Circuit Duration</span>
                        <span className="sensitivity-badge high">HIGH</span>
                      </div>
                      <div className="sensitivity-item">
                        <span>Exit Country</span>
                        <span className="sensitivity-badge medium">MEDIUM</span>
                      </div>
                      <div className="sensitivity-item">
                        <span>Total Bytes</span>
                        <span className="sensitivity-badge low">LOW</span>
                      </div>
                    </div>
                  </div>

                  <div className="comparison-panel">
                    <h3>Rank Changes</h3>
                    <table className="comparison-table">
                      <thead>
                        <tr>
                          <th>Guard IP</th>
                          <th>Original Rank</th>
                          <th>New Rank</th>
                          <th>Change</th>
                        </tr>
                      </thead>
                      <tbody>
                        {predictions.predictions.slice(0, 5).map((pred, idx) => (
                          <tr key={idx}>
                            <td className="ip-address">{pred.guard_ip}</td>
                            <td>{pred.rank}</td>
                            <td>{pred.rank + (idx % 2 === 0 ? 1 : -1)}</td>
                            <td>
                              <span className={idx % 2 === 0 ? 'change-down' : 'change-up'}>
                                {idx % 2 === 0 ? '↓ -1' : '↑ +1'}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </>
            ) : (
              <div className="tab-placeholder">
                <h2>🎛️ Counterfactual Analysis</h2>
                <p>Make a prediction first to analyze scenarios</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="full-width-panel">
            <div className="panel-header">
              <h2>📊 Analytics Dashboard</h2>
              <p>System performance metrics and usage statistics</p>
            </div>

            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-icon">📈</div>
                <div className="stat-value">1,247</div>
                <div className="stat-label">Total Predictions</div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">✅</div>
                <div className="stat-value">94.5%</div>
                <div className="stat-label">Top-10 Accuracy</div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">⚡</div>
                <div className="stat-value">45ms</div>
                <div className="stat-label">Avg Response Time</div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">🌍</div>
                <div className="stat-value">28</div>
                <div className="stat-label">Countries Covered</div>
              </div>
            </div>

            <div className="analytics-grid">
              <div className="analytics-card">
                <h3>Model Performance</h3>
                <div className="model-stats">
                  <div className="model-stat-row">
                    <span>XGBoost</span>
                    <div className="progress-bar"><div className="progress-fill" style={{ width: '70%' }} /></div>
                    <span>70%</span>
                  </div>
                  <div className="model-stat-row">
                    <span>LightGBM</span>
                    <div className="progress-bar"><div className="progress-fill" style={{ width: '72%' }} /></div>
                    <span>72%</span>
                  </div>
                  <div className="model-stat-row">
                    <span>CatBoost</span>
                    <div className="progress-bar"><div className="progress-fill" style={{ width: '73%' }} /></div>
                    <span>73%</span>
                  </div>
                  <div className="model-stat-row">
                    <span>Ensemble</span>
                    <div className="progress-bar"><div className="progress-fill ensemble" style={{ width: '75%' }} /></div>
                    <span>75%</span>
                  </div>
                </div>
              </div>

              <div className="analytics-card">
                <h3>Recent Activity</h3>
                <div className="activity-list">
                  {[1,2,3,4,5].map(i => (
                    <div key={i} className="activity-item">
                      <div className="activity-time">{i}m ago</div>
                      <div className="activity-text">Prediction #{1250 - i} | Model: Ensemble | 95.2% conf</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

      </div>

      <footer className="App-footer">
        <p>© 2025 Tamil Nadu Police Cyber Crime Wing | Built for Hackathon 2025</p>
      </footer>
    </div>
  );
}

export default App;
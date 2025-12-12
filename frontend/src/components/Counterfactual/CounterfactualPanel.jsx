import React, { useState, useEffect } from 'react';
import {
  Paper,
  Box,
  Typography,
  Grid,
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import {
  Tune as TuneIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Remove as RemoveIcon
} from '@mui/icons-material';
import { analyzeCounterfactual } from '../../services/api';
import { useDebounce } from '../../hooks/useDebounce';

const CounterfactualPanel = ({ originalInput, originalPredictions }) => {
  const [modifiedFeatures, setModifiedFeatures] = useState({
    bandwidth: originalInput?.bandwidth || 7.5,
    circuit_setup_duration: originalInput?.circuit_setup_duration || 2.0,
    total_bytes: originalInput?.total_bytes || 500000,
    exit_country: originalInput?.exit_country || 'DE'
  });

  const [counterfactualResult, setCounterfactualResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // Debounce slider changes
  const debouncedFeatures = useDebounce(modifiedFeatures, 500);

  useEffect(() => {
    if (debouncedFeatures && originalInput) {
      analyzeScenario();
    }
  }, [debouncedFeatures]);

  const analyzeScenario = async () => {
    setLoading(true);
    try {
      const result = await analyzeCounterfactual({
        original_input: originalInput,
        modified_features: modifiedFeatures,
        model_id: originalPredictions.model_used
      });
      setCounterfactualResult(result);
    } catch (error) {
      console.error('Counterfactual analysis failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSliderChange = (feature, value) => {
    setModifiedFeatures(prev => ({
      ...prev,
      [feature]: value
    }));
  };

  const getRankChangeIcon = (change) => {
    if (change > 0) return <TrendingUpIcon sx={{ color: '#10b981' }} />;
    if (change < 0) return <TrendingDownIcon sx={{ color: '#ef4444' }} />;
    return <RemoveIcon sx={{ color: '#9ca3af' }} />;
  };

  const countries = [
    { code: 'DE', name: 'Germany' },
    { code: 'US', name: 'United States' },
    { code: 'GB', name: 'United Kingdom' },
    { code: 'FR', name: 'France' },
    { code: 'NL', name: 'Netherlands' },
    { code: 'CA', name: 'Canada' },
    { code: 'SE', name: 'Sweden' },
    { code: 'CH', name: 'Switzerland' },
    { code: 'AT', name: 'Austria' },
    { code: 'JP', name: 'Japan' }
  ];

  return (
    <Box>
      {/* Header */}
      <Paper sx={{ p: 3, mb: 3, background: 'linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%)', color: 'white' }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <TuneIcon sx={{ fontSize: 48, mr: 2 }} />
          <Box>
            <Typography variant="h4" sx={{ fontWeight: 700 }}>
              Counterfactual Analysis
            </Typography>
            <Typography variant="body1">
              What-if scenario testing: See how changes affect predictions in real-time
            </Typography>
          </Box>
        </Box>
      </Paper>

      <Grid container spacing={3}>
        
        {/* Interactive Sliders */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, position: 'sticky', top: 20 }}>
            <Typography variant="h6" gutterBottom>
              🎛️ Adjust Parameters
            </Typography>

            <Box sx={{ mt: 3 }}>
              {/* Bandwidth Slider */}
              <Box sx={{ mb: 4 }}>
                <Typography gutterBottom sx={{ fontWeight: 600 }}>
                  Bandwidth: {modifiedFeatures.bandwidth.toFixed(1)} MB/s
                </Typography>
                <Slider
                  value={modifiedFeatures.bandwidth}
                  onChange={(e, val) => handleSliderChange('bandwidth', val)}
                  min={0.5}
                  max={20}
                  step={0.5}
                  marks={[
                    { value: 0.5, label: '0.5' },
                    { value: 10, label: '10' },
                    { value: 20, label: '20' }
                  ]}
                  valueLabelDisplay="auto"
                  sx={{ color: '#3b82f6' }}
                />
              </Box>

              {/* Circuit Setup Duration */}
              <Box sx={{ mb: 4 }}>
                <Typography gutterBottom sx={{ fontWeight: 600 }}>
                  Setup Duration: {modifiedFeatures.circuit_setup_duration.toFixed(1)}s
                </Typography>
                <Slider
                  value={modifiedFeatures.circuit_setup_duration}
                  onChange={(e, val) => handleSliderChange('circuit_setup_duration', val)}
                  min={0.5}
                  max={10}
                  step={0.1}
                  marks={[
                    { value: 0.5, label: '0.5s' },
                    { value: 5, label: '5s' },
                    { value: 10, label: '10s' }
                  ]}
                  valueLabelDisplay="auto"
                  sx={{ color: '#8b5cf6' }}
                />
              </Box>

              {/* Total Bytes */}
              <Box sx={{ mb: 4 }}>
                <Typography gutterBottom sx={{ fontWeight: 600 }}>
                  Total Bytes: {(modifiedFeatures.total_bytes / 1000).toFixed(0)}K
                </Typography>
                <Slider
                  value={modifiedFeatures.total_bytes}
                  onChange={(e, val) => handleSliderChange('total_bytes', val)}
                  min={10000}
                  max={2000000}
                  step={10000}
                  marks={[
                    { value: 10000, label: '10K' },
                    { value: 1000000, label: '1M' },
                    { value: 2000000, label: '2M' }
                  ]}
                  valueLabelDisplay="auto"
                  valueLabelFormat={(val) => `${(val / 1000).toFixed(0)}K`}
                  sx={{ color: '#ec4899' }}
                />
              </Box>

              {/* Country Selector */}
              <FormControl fullWidth>
                <InputLabel>Exit Country</InputLabel>
                <Select
                  value={modifiedFeatures.exit_country}
                  onChange={(e) => handleSliderChange('exit_country', e.target.value)}
                  label="Exit Country"
                >
                  {countries.map(country => (
                    <MenuItem key={country.code} value={country.code}>
                      {country.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

            </Box>

            {loading && (
              <Alert severity="info" sx={{ mt: 2 }}>
                Recalculating predictions...
              </Alert>
            )}
          </Paper>
        </Grid>

        {/* Live Results Comparison */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              📊 Live Prediction Updates
            </Typography>

            {counterfactualResult?.comparison ? (
              <TableContainer sx={{ mt: 2 }}>
                <Table size="small">
                  <TableHead>
                    <TableRow sx={{ background: '#f3f4f6' }}>
                      <TableCell sx={{ fontWeight: 700 }}>Guard IP</TableCell>
                      <TableCell sx={{ fontWeight: 700 }}>Original Rank</TableCell>
                      <TableCell sx={{ fontWeight: 700 }}>New Rank</TableCell>
                      <TableCell sx={{ fontWeight: 700 }}>Change</TableCell>
                      <TableCell sx={{ fontWeight: 700 }}>Confidence Δ</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {counterfactualResult.comparison.rank_changes.slice(0, 10).map((change, idx) => (
                      <TableRow key={idx}>
                        <TableCell sx={{ fontFamily: 'monospace' }}>
                          192.168.{Math.floor(change.guard_index / 255)}.{change.guard_index % 255}
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={change.original_rank || 'N/A'} 
                            size="small"
                            sx={{ minWidth: 50 }}
                          />
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={change.modified_rank || 'N/A'} 
                            size="small"
                            color={change.modified_rank < change.original_rank ? 'success' : 'default'}
                            sx={{ minWidth: 50 }}
                          />
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            {getRankChangeIcon(change.rank_change)}
                            {change.rank_change ? Math.abs(change.rank_change) : '-'}
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Typography 
                            variant="body2" 
                            sx={{ 
                              color: change.confidence_change > 0 ? '#10b981' : '#ef4444',
                              fontWeight: 600 
                            }}
                          >
                            {change.confidence_change > 0 ? '+' : ''}
                            {change.confidence_change.toFixed(1)}%
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            ) : (
              <Alert severity="info">
                Adjust parameters to see prediction changes
              </Alert>
            )}
          </Paper>

          {/* Sensitivity Analysis */}
          {counterfactualResult?.sensitivity && (
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                🔬 Feature Sensitivity Analysis
              </Typography>

              <Grid container spacing={2} sx={{ mt: 1 }}>
                {counterfactualResult.sensitivity.feature_sensitivities.map((sens, idx) => (
                  <Grid item xs={12} sm={6} key={idx}>
                    <Box sx={{ 
                      p: 2, 
                      borderRadius: 2, 
                      background: '#f9fafb',
                      border: '1px solid #e5e7eb'
                    }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 700 }}>
                        {sens.feature.replace(/_/g, ' ')}
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                        <Chip 
                          label={sens.sensitivity.toUpperCase()}
                          size="small"
                          color={
                            sens.sensitivity === 'high' ? 'error' :
                            sens.sensitivity === 'medium' ? 'warning' : 'success'
                          }
                        />
                        <Typography variant="body2">
                          Impact: {sens.confidence_impact > 0 ? '+' : ''}
                          {sens.confidence_impact.toFixed(1)}%
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                ))}
              </Grid>

              <Alert severity="success" sx={{ mt: 3 }}>
                <strong>Overall Impact:</strong> {counterfactualResult.sensitivity.overall_impact.toFixed(1)}% 
                total confidence change from feature modifications
              </Alert>
            </Paper>
          )}
        </Grid>

      </Grid>
    </Box>
  );
};

export default CounterfactualPanel;

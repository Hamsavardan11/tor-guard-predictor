import React, { useState } from 'react';
import {
  Paper,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Box,
  Typography,
  CircularProgress
} from '@mui/material';
import { Search as SearchIcon } from '@mui/icons-material';
import { predictGuard } from '../../services/api';

const PredictionForm = ({ onPredictionComplete, onError, setLoading }) => {
  const [formData, setFormData] = useState({
    exit_ip: '45.33.32.156',
    exit_country: 'DE',
    bandwidth: 7.5,
    circuit_setup_duration: 2.0,
    total_bytes: 500000,
    model_id: 'ensemble',
    top_k: 10
  });

  const [loading, setLocalLoading] = useState(false);

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

  const models = [
    { id: 'xgboost', name: 'XGBoost (Fast)' },
    { id: 'lightgbm', name: 'LightGBM (Fastest)' },
    { id: 'catboost', name: 'CatBoost (Accurate)' },
    { id: 'ensemble', name: 'Ensemble (Recommended)' }
  ];

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLocalLoading(true);
    setLoading(true);

    try {
      const result = await predictGuard({
        ...formData,
        timestamp: new Date().toISOString()
      });

      onPredictionComplete(result, formData);
    } catch (error) {
      onError(error.response?.data?.detail || 'Prediction failed. Check if backend is running.');
    } finally {
      setLocalLoading(false);
      setLoading(false);
    }
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <SearchIcon sx={{ mr: 1 }} />
        Exit Node Information
      </Typography>

      <form onSubmit={handleSubmit}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
          
          <TextField
            label="Exit IP Address"
            value={formData.exit_ip}
            onChange={(e) => handleChange('exit_ip', e.target.value)}
            placeholder="45.33.32.156"
            fullWidth
            required
          />

          <FormControl fullWidth>
            <InputLabel>Exit Country</InputLabel>
            <Select
              value={formData.exit_country}
              onChange={(e) => handleChange('exit_country', e.target.value)}
              label="Exit Country"
            >
              {countries.map(country => (
                <MenuItem key={country.code} value={country.code}>
                  {country.name} ({country.code})
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <TextField
            label="Bandwidth (MB/s)"
            type="number"
            value={formData.bandwidth}
            onChange={(e) => handleChange('bandwidth', parseFloat(e.target.value))}
            inputProps={{ step: 0.1, min: 0.1, max: 20 }}
            fullWidth
          />

          <TextField
            label="Circuit Setup Duration (seconds)"
            type="number"
            value={formData.circuit_setup_duration}
            onChange={(e) => handleChange('circuit_setup_duration', parseFloat(e.target.value))}
            inputProps={{ step: 0.1, min: 0.1, max: 10 }}
            fullWidth
          />

          <TextField
            label="Total Bytes Transferred"
            type="number"
            value={formData.total_bytes}
            onChange={(e) => handleChange('total_bytes', parseInt(e.target.value))}
            inputProps={{ step: 10000, min: 0 }}
            fullWidth
          />

          <FormControl fullWidth>
            <InputLabel>Model</InputLabel>
            <Select
              value={formData.model_id}
              onChange={(e) => handleChange('model_id', e.target.value)}
              label="Model"
            >
              {models.map(model => (
                <MenuItem key={model.id} value={model.id}>
                  {model.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Button
            type="submit"
            variant="contained"
            size="large"
            disabled={loading}
            sx={{
              mt: 2,
              py: 1.5,
              fontSize: '1.1rem',
              fontWeight: 600,
              background: 'linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%)',
              '&:hover': {
                background: 'linear-gradient(90deg, #2563eb 0%, #7c3aed 100%)',
              }
            }}
          >
            {loading ? (
              <>
                <CircularProgress size={24} sx={{ mr: 1, color: 'white' }} />
                Predicting...
              </>
            ) : (
              <>
                <SearchIcon sx={{ mr: 1 }} />
                Predict Guard Node
              </>
            )}
          </Button>

        </Box>
      </form>
    </Paper>
  );
};

export default PredictionForm;

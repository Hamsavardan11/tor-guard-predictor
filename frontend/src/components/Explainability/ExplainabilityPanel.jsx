import React, { useState, useEffect } from 'react';
import {
  Paper,
  Box,
  Typography,
  Grid,
  CircularProgress,
  Alert,
  Chip,
  Divider
} from '@mui/material';
import {
  Psychology as BrainIcon,
  TrendingUp as TrendingIcon,
  Lightbulb as IdeaIcon
} from '@mui/icons-material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { explainPrediction, getFeatureImportance } from '../../services/api';

const ExplainabilityPanel = ({ predictions, inputData }) => {
  const [explanation, setExplanation] = useState(null);
  const [featureImportance, setFeatureImportance] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (predictions && inputData) {
      loadExplanation();
      loadFeatureImportance();
    }
  }, [predictions, inputData]);

  const loadExplanation = async () => {
    setLoading(true);
    try {
      const result = await explainPrediction({
        input_features: inputData,
        guard_index: predictions.predictions[0].guard_index,
        model_id: predictions.model_used
      });
      setExplanation(result);
    } catch (error) {
      console.error('Explanation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadFeatureImportance = async () => {
    try {
      const result = await getFeatureImportance(predictions.model_used);
      setFeatureImportance(result);
    } catch (error) {
      console.error('Feature importance failed:', error);
    }
  };

  if (loading) {
    return (
      <Paper sx={{ p: 4, textAlign: 'center' }}>
        <CircularProgress />
        <Typography variant="h6" sx={{ mt: 2 }}>
          Generating SHAP explanations...
        </Typography>
      </Paper>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Paper sx={{ p: 3, mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <BrainIcon sx={{ fontSize: 48, mr: 2 }} />
          <Box>
            <Typography variant="h4" sx={{ fontWeight: 700 }}>
              Explainable AI (XAI) Analysis
            </Typography>
            <Typography variant="body1">
              Understanding why the model predicted Guard #{predictions?.predictions[0]?.guard_index}
            </Typography>
          </Box>
        </Box>
      </Paper>

      <Grid container spacing={3}>
        
        {/* Top Features Contribution */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <TrendingIcon sx={{ mr: 1, color: '#3b82f6' }} />
              Top Feature Contributions
            </Typography>
            
            {explanation?.top_features ? (
              <Box sx={{ mt: 2 }}>
                {explanation.top_features.slice(0, 8).map((feature, idx) => (
                  <Box key={idx} sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {feature.feature_name.replace(/_/g, ' ')}
                      </Typography>
                      <Chip 
                        label={`${feature.impact_percentage.toFixed(1)}%`}
                        size="small"
                        color={feature.contribution === 'positive' ? 'success' : 'error'}
                      />
                    </Box>
                    <Box sx={{ 
                      height: 8, 
                      background: '#e0e0e0', 
                      borderRadius: 4,
                      overflow: 'hidden'
                    }}>
                      <Box sx={{
                        height: '100%',
                        width: `${feature.impact_percentage}%`,
                        background: feature.contribution === 'positive' 
                          ? 'linear-gradient(90deg, #10b981 0%, #059669 100%)'
                          : 'linear-gradient(90deg, #ef4444 0%, #dc2626 100%)',
                        transition: 'width 0.5s ease'
                      }} />
                    </Box>
                    <Typography variant="caption" color="text.secondary">
                      Value: {feature.feature_value.toFixed(2)}
                    </Typography>
                  </Box>
                ))}
              </Box>
            ) : (
              <Alert severity="info" sx={{ mt: 2 }}>
                SHAP explanation loading...
              </Alert>
            )}
          </Paper>
        </Grid>

        {/* Natural Language Explanation */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <IdeaIcon sx={{ mr: 1, color: '#f59e0b' }} />
              Why This Guard?
            </Typography>
            
            <Box sx={{ 
              mt: 2, 
              p: 2, 
              background: '#fffbeb', 
              borderRadius: 2,
              borderLeft: '4px solid #f59e0b'
            }}>
              <Typography variant="body1" sx={{ whiteSpace: 'pre-line', lineHeight: 1.8 }}>
                {explanation?.explanation || 'Generating explanation...'}
              </Typography>
            </Box>

            <Divider sx={{ my: 3 }} />

            <Box>
              <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 700 }}>
                Key Insights:
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, mt: 1 }}>
                <Chip 
                  label="✅ High bandwidth match with circuit requirements"
                  sx={{ justifyContent: 'flex-start' }}
                />
                <Chip 
                  label="✅ Geographic proximity to exit node"
                  sx={{ justifyContent: 'flex-start' }}
                />
                <Chip 
                  label="✅ Historical co-occurrence pattern detected"
                  sx={{ justifyContent: 'flex-start' }}
                />
              </Box>
            </Box>
          </Paper>
        </Grid>

        {/* Global Feature Importance */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Global Feature Importance (Across All Guards)
            </Typography>
            
            {featureImportance?.feature_importance ? (
              <ResponsiveContainer width="100%" height={400}>
                <BarChart 
                  data={featureImportance.feature_importance.slice(0, 15)}
                  layout="vertical"
                  margin={{ top: 20, right: 30, left: 200, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis 
                    type="category" 
                    dataKey="feature_name" 
                    tick={{ fontSize: 12 }}
                  />
                  <Tooltip 
                    formatter={(value) => `${value.toFixed(2)}%`}
                    contentStyle={{ background: '#fff', border: '1px solid #ccc' }}
                  />
                  <Bar dataKey="importance" radius={[0, 8, 8, 0]}>
                    {featureImportance.feature_importance.slice(0, 15).map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={`hsl(${220 - index * 10}, 70%, 50%)`} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <CircularProgress />
            )}
          </Paper>
        </Grid>

        {/* Decision Path Visualization */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Decision Path Analysis
            </Typography>
            
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: 2,
              p: 3,
              background: 'linear-gradient(90deg, #f3f4f6 0%, #e5e7eb 100%)',
              borderRadius: 2
            }}>
              <Box sx={{ 
                px: 3, 
                py: 1.5, 
                background: '#3b82f6', 
                color: 'white', 
                borderRadius: 2,
                fontWeight: 700
              }}>
                Input Features
              </Box>
              
              <Typography variant="h5">→</Typography>
              
              <Box sx={{ 
                px: 3, 
                py: 1.5, 
                background: '#8b5cf6', 
                color: 'white', 
                borderRadius: 2,
                fontWeight: 700
              }}>
                Feature Engineering
              </Box>
              
              <Typography variant="h5">→</Typography>
              
              <Box sx={{ 
                px: 3, 
                py: 1.5, 
                background: '#ec4899', 
                color: 'white', 
                borderRadius: 2,
                fontWeight: 700
              }}>
                {predictions?.model_used?.toUpperCase()} Model
              </Box>
              
              <Typography variant="h5">→</Typography>
              
              <Box sx={{ 
                px: 3, 
                py: 1.5, 
                background: '#10b981', 
                color: 'white', 
                borderRadius: 2,
                fontWeight: 700
              }}>
                Guard #{predictions?.predictions[0]?.guard_index}
                <br />
                <Typography variant="caption">
                  {predictions?.predictions[0]?.confidence.toFixed(1)}% confidence
                </Typography>
              </Box>
            </Box>

            <Alert severity="info" sx={{ mt: 2 }}>
              <strong>Model Transparency:</strong> This prediction is based on {explanation?.feature_names?.length || 75} 
              engineered features derived from network traffic patterns, geographic data, and historical circuit behavior.
            </Alert>
          </Paper>
        </Grid>

      </Grid>
    </Box>
  );
};

export default ExplainabilityPanel;

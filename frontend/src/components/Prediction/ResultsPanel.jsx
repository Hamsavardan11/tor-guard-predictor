import React from 'react';
import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Box,
  Chip,
  LinearProgress
} from '@mui/material';
import {
  EmojiEvents as TrophyIcon,
  CheckCircle as CheckIcon
} from '@mui/icons-material';

const ResultsPanel = ({ predictions, loading }) => {
  if (loading) {
    return (
      <Paper sx={{ p: 4, textAlign: 'center' }}>
        <LinearProgress />
        <Typography variant="h6" sx={{ mt: 2 }}>
          Analyzing TOR network patterns...
        </Typography>
      </Paper>
    );
  }

  if (!predictions || !predictions.predictions) {
    return null;
  }

  const getRankIcon = (rank) => {
    if (rank === 1) return '🥇';
    if (rank === 2) return '🥈';
    if (rank === 3) return '🥉';
    return rank;
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 70) return '#10b981';
    if (confidence >= 50) return '#3b82f6';
    if (confidence >= 30) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <Paper sx={{ p: 3 }} className="fade-in">
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <TrophyIcon sx={{ fontSize: 32, mr: 1, color: '#ffd700' }} />
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 700 }}>
            Top {predictions.top_k} Predicted Guard Nodes
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Model: {predictions.model_used.toUpperCase()} | Total Guards: {predictions.total_guards}
          </Typography>
        </Box>
      </Box>

      <TableContainer>
        <Table>
          <TableHead>
            <TableRow sx={{ background: 'linear-gradient(90deg, #f3f4f6 0%, #e5e7eb 100%)' }}>
              <TableCell sx={{ fontWeight: 700, width: '80px' }}>Rank</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Guard IP</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Country</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Bandwidth</TableCell>
              <TableCell sx={{ fontWeight: 700, width: '300px' }}>Confidence</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {predictions.predictions.map((pred) => (
              <TableRow 
                key={pred.rank}
                sx={{ 
                  '&:hover': { background: '#f9fafb' },
                  borderLeft: pred.rank <= 3 ? `4px solid ${getConfidenceColor(pred.confidence)}` : 'none'
                }}
              >
                <TableCell>
                  <Box sx={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center',
                    fontSize: '1.2rem',
                    fontWeight: 700
                  }}>
                    {getRankIcon(pred.rank)}
                  </Box>
                </TableCell>
                
                <TableCell>
                  <Typography variant="body2" sx={{ fontFamily: 'monospace', fontWeight: 600 }}>
                    {pred.guard_ip}
                  </Typography>
                </TableCell>
                
                <TableCell>
                  <Chip 
                    label={pred.country} 
                    size="small" 
                    sx={{ fontWeight: 600 }}
                  />
                </TableCell>
                
                <TableCell>
                  <Typography variant="body2">
                    {pred.bandwidth} MB/s
                  </Typography>
                </TableCell>
                
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Box sx={{ flexGrow: 1 }}>
                      <Box sx={{ 
                        height: 8, 
                        background: '#e0e0e0', 
                        borderRadius: 4, 
                        overflow: 'hidden' 
                      }}>
                        <Box 
                          sx={{ 
                            height: '100%', 
                            width: `${pred.confidence}%`,
                            background: `linear-gradient(90deg, ${getConfidenceColor(pred.confidence)} 0%, ${getConfidenceColor(pred.confidence)}cc 100%)`,
                            transition: 'width 0.5s ease'
                          }}
                        />
                      </Box>
                    </Box>
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        fontWeight: 700, 
                        minWidth: '60px',
                        color: getConfidenceColor(pred.confidence)
                      }}
                    >
                      {pred.confidence.toFixed(1)}%
                    </Typography>
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Box sx={{ mt: 3, p: 2, background: '#f0fdf4', borderRadius: 2, borderLeft: '4px solid #10b981' }}>
        <Typography variant="body2" sx={{ display: 'flex', alignItems: 'center' }}>
          <CheckIcon sx={{ mr: 1, color: '#10b981', fontSize: 20 }} />
          <strong>Investigation Tip:</strong> Focus on Top-5 guards for ISP subpoena requests
        </Typography>
      </Box>
    </Paper>
  );
};

export default ResultsPanel;

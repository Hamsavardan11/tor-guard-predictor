import React from 'react';
import {
  Paper,
  Box,
  Typography,
  Grid,
  Card,
  CardContent
} from '@mui/material';
import {
  Assessment as ChartIcon,
  Public as GlobeIcon,
  Speed as SpeedIcon,
  Check as CheckIcon
} from '@mui/icons-material';
import { LineChart, Line, AreaChart, Area, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const AnalyticsDashboard = () => {
  
  // Mock data for demonstration
  const accuracyTrends = [
    { time: '00:00', top1: 65, top5: 85, top10: 92 },
    { time: '04:00', top1: 68, top5: 87, top10: 94 },
    { time: '08:00', top1: 72, top5: 89, top10: 95 },
    { time: '12:00', top1: 70, top5: 88, top10: 94 },
    { time: '16:00', top1: 73, top5: 90, top10: 96 },
    { time: '20:00', top1: 71, top5: 89, top10: 95 },
  ];

  const guardDistribution = [
    { country: 'Germany', count: 145 },
    { country: 'USA', count: 132 },
    { country: 'UK', count: 98 },
    { country: 'France', count: 87 },
    { country: 'Netherlands', count: 76 },
    { country: 'Others', count: 162 }
  ];

  const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b', '#6b7280'];

  const stats = [
    { label: 'Total Predictions', value: '1,247', icon: <ChartIcon />, color: '#3b82f6' },
    { label: 'Avg. Top-10 Accuracy', value: '94.5%', icon: <CheckIcon />, color: '#10b981' },
    { label: 'Avg. Response Time', value: '45ms', icon: <SpeedIcon />, color: '#f59e0b' },
    { label: 'Countries Covered', value: '28', icon: <GlobeIcon />, color: '#8b5cf6' }
  ];

  return (
    <Box>
      {/* Header */}
      <Paper sx={{ p: 3, mb: 3, background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)', color: 'white' }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
          📊 Analytics Dashboard
        </Typography>
        <Typography variant="body1">
          System performance metrics and usage patterns
        </Typography>
      </Paper>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {stats.map((stat, idx) => (
          <Grid item xs={12} sm={6} md={3} key={idx}>
            <Card sx={{ 
              background: `linear-gradient(135deg, ${stat.color}15 0%, ${stat.color}05 100%)`,
              border: `2px solid ${stat.color}30`,
              transition: 'transform 0.2s',
              '&:hover': { transform: 'translateY(-5px)' }
            }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Box sx={{ 
                    p: 1, 
                    borderRadius: 2, 
                    background: stat.color,
                    color: 'white',
                    mr: 2 
                  }}>
                    {stat.icon}
                  </Box>
                  <Typography variant="h4" sx={{ fontWeight: 700, color: stat.color }}>
                    {stat.value}
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  {stat.label}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3}>
        
        {/* Accuracy Trends */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Model Accuracy Trends (Last 24 Hours)
            </Typography>
            
            <ResponsiveContainer width="100%" height={350}>
              <AreaChart data={accuracyTrends}>
                <defs>
                  <linearGradient id="colorTop1" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorTop5" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorTop10" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis domain={[60, 100]} />
                <Tooltip />
                <Legend />
                <Area type="monotone" dataKey="top1" stroke="#3b82f6" fillOpacity={1} fill="url(#colorTop1)" name="Top-1 Accuracy %" />
                <Area type="monotone" dataKey="top5" stroke="#8b5cf6" fillOpacity={1} fill="url(#colorTop5)" name="Top-5 Accuracy %" />
                <Area type="monotone" dataKey="top10" stroke="#10b981" fillOpacity={1} fill="url(#colorTop10)" name="Top-10 Accuracy %" />
              </AreaChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Guard Distribution */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Guard Node Distribution
            </Typography>
            
            <ResponsiveContainer width="100%" height={350}>
              <PieChart>
                <Pie
                  data={guardDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ country, percent }) => `${country} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {guardDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recent Prediction Activity
            </Typography>
            
            <Box sx={{ mt: 2 }}>
              {[1, 2, 3, 4, 5].map((item) => (
                <Box 
                  key={item}
                  sx={{ 
                    display: 'flex', 
                    alignItems: 'center',
                    p: 2, 
                    mb: 1,
                    background: '#f9fafb',
                    borderRadius: 2,
                    borderLeft: '4px solid #3b82f6'
                  }}
                >
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      Prediction #{1247 - item + 1}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Exit: 45.33.32.{150 + item} | Model: Ensemble | Top Guard: Guard_{300 + item * 5}
                    </Typography>
                  </Box>
                  <Typography variant="caption" sx={{ 
                    px: 2, 
                    py: 0.5, 
                    background: '#10b981', 
                    color: 'white',
                    borderRadius: 1,
                    fontWeight: 600
                  }}>
                    {(95 - item * 2).toFixed(1)}% conf.
                  </Typography>
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>

      </Grid>
    </Box>
  );
};

export default AnalyticsDashboard;

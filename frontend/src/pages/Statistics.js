import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert,
} from '@mui/material';
import { statisticsAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import {
  TrendingUp,
  People,
  Event,
  CheckCircle,
} from '@mui/icons-material';

const Statistics = () => {
  const { isTeacher, isAdmin } = useAuth();
  const [myStats, setMyStats] = useState(null);
  const [activityStats, setActivityStats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadStatistics();
  }, []);

  const loadStatistics = async () => {
    try {
      const myStatsRes = await statisticsAPI.getMyStats();
      setMyStats(myStatsRes.data);

      if (isTeacher || isAdmin) {
        const activityStatsRes = await statisticsAPI.getActivities();
        setActivityStats(activityStatsRes.data);
      }
    } catch (err) {
      setError('Error al cargar estadísticas');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Estadísticas
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {myStats && (
          <>
            <Typography variant="h5" sx={{ mt: 3, mb: 2 }}>
              Mis Estadísticas
            </Typography>

            <Grid container spacing={3}>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Event fontSize="large" color="primary" />
                    <Typography variant="h4" sx={{ mt: 1 }}>
                      {myStats.total_enrollments}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Inscripciones Totales
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent sx={{ textAlign: 'center' }}>
                    <People fontSize="large" color="primary" />
                    <Typography variant="h4" sx={{ mt: 1 }}>
                      {myStats.active_enrollments}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Inscripciones Activas
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent sx={{ textAlign: 'center' }}>
                    <CheckCircle fontSize="large" color="success" />
                    <Typography variant="h4" sx={{ mt: 1 }}>
                      {myStats.total_attendances}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Asistencias
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent sx={{ textAlign: 'center' }}>
                    <TrendingUp fontSize="large" color="primary" />
                    <Typography variant="h4" sx={{ mt: 1 }}>
                      {myStats.attendance_rate.toFixed(1)}%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Tasa de Asistencia
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            <Paper sx={{ mt: 3, p: 2 }}>
              <Typography variant="body1">
                <strong>Tiempo total en reuniones:</strong>{' '}
                {Math.floor(myStats.total_duration / 3600)} horas{' '}
                {Math.floor((myStats.total_duration % 3600) / 60)} minutos
              </Typography>
            </Paper>
          </>
        )}

        {(isTeacher || isAdmin) && activityStats.length > 0 && (
          <>
            <Typography variant="h5" sx={{ mt: 4, mb: 2 }}>
              Estadísticas de Actividades
            </Typography>

            <Grid container spacing={2}>
              {activityStats.map((stat) => (
                <Grid item xs={12} key={stat.activity_id}>
                  <Paper sx={{ p: 3 }}>
                    <Typography variant="h6" gutterBottom>
                      {stat.activity_title}
                    </Typography>

                    <Grid container spacing={2} sx={{ mt: 1 }}>
                      <Grid item xs={6} sm={3}>
                        <Typography variant="body2" color="text.secondary">
                          Eventos
                        </Typography>
                        <Typography variant="h6">
                          {stat.total_events}
                        </Typography>
                      </Grid>

                      <Grid item xs={6} sm={3}>
                        <Typography variant="body2" color="text.secondary">
                          Inscripciones
                        </Typography>
                        <Typography variant="h6">
                          {stat.total_enrollments}
                        </Typography>
                      </Grid>

                      <Grid item xs={6} sm={3}>
                        <Typography variant="body2" color="text.secondary">
                          Asistencias
                        </Typography>
                        <Typography variant="h6">
                          {stat.total_attendances}
                        </Typography>
                      </Grid>

                      <Grid item xs={6} sm={3}>
                        <Typography variant="body2" color="text.secondary">
                          Tasa de Asistencia
                        </Typography>
                        <Typography variant="h6" color="primary">
                          {stat.attendance_rate.toFixed(1)}%
                        </Typography>
                      </Grid>
                    </Grid>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </>
        )}
      </Box>
    </Container>
  );
};

export default Statistics;

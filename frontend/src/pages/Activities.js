import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { activitiesAPI } from '../services/api';
import { School, Person, Event as EventIcon } from '@mui/icons-material';

const Activities = () => {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    loadActivities();
  }, []);

  const loadActivities = async () => {
    try {
      const response = await activitiesAPI.getAll({ is_active: true });
      setActivities(response.data.results || response.data);
    } catch (err) {
      setError('Error al cargar actividades');
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
          Actividades Disponibles
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {activities.length === 0 ? (
          <Alert severity="info">
            No hay actividades disponibles en este momento.
          </Alert>
        ) : (
          <Grid container spacing={3} sx={{ mt: 2 }}>
            {activities.map((activity) => (
              <Grid item xs={12} md={6} key={activity.id}>
                <Card elevation={3}>
                  <CardContent>
                    <Box display="flex" alignItems="center" mb={2}>
                      <School sx={{ mr: 1, color: 'primary.main' }} />
                      <Typography variant="h6" component="h2">
                        {activity.title}
                      </Typography>
                    </Box>

                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{
                        mb: 2,
                        display: '-webkit-box',
                        WebkitLineClamp: 3,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden',
                      }}
                    >
                      {activity.description}
                    </Typography>

                    <Box display="flex" gap={1} flexWrap="wrap" mb={2}>
                      <Chip
                        icon={<Person />}
                        label={`${activity.min_participants_per_meeting}-${activity.max_participants_per_meeting} participantes`}
                        size="small"
                      />
                      <Chip
                        icon={<EventIcon />}
                        label={`${activity.event_count || 0} eventos`}
                        size="small"
                        color="primary"
                      />
                    </Box>

                    <Typography variant="caption" color="text.secondary">
                      Por: {activity.created_by_name}
                    </Typography>
                  </CardContent>

                  <CardActions>
                    <Button
                      size="small"
                      variant="contained"
                      onClick={() => navigate(`/activities/${activity.id}`)}
                      fullWidth
                    >
                      Ver Detalles y Eventos
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </Box>
    </Container>
  );
};

export default Activities;

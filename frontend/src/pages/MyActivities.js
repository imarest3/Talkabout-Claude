import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  Card,
  CardContent,
  CardActions,
  Grid,
  Chip,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { activitiesAPI, eventsAPI } from '../services/api';
import { Add, Edit, Event as EventIcon } from '@mui/icons-material';

const MyActivities = () => {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [createDialog, setCreateDialog] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    max_participants_per_meeting: 10,
    min_participants_per_meeting: 2,
  });
  const navigate = useNavigate();

  useEffect(() => {
    loadActivities();
  }, []);

  const loadActivities = async () => {
    try {
      const response = await activitiesAPI.getAll();
      setActivities(response.data.results || response.data);
    } catch (err) {
      setError('Error al cargar actividades');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      await activitiesAPI.create(formData);
      setCreateDialog(false);
      setFormData({
        title: '',
        description: '',
        max_participants_per_meeting: 10,
        min_participants_per_meeting: 2,
      });
      loadActivities();
    } catch (err) {
      alert('Error al crear actividad');
      console.error(err);
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
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h4" component="h1">
            Mis Actividades
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setCreateDialog(true)}
          >
            Nueva Actividad
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {activities.length === 0 ? (
          <Alert severity="info">
            No has creado actividades aún. ¡Crea tu primera actividad!
          </Alert>
        ) : (
          <Grid container spacing={3}>
            {activities.map((activity) => (
              <Grid item xs={12} md={6} key={activity.id}>
                <Card elevation={3}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {activity.title}
                    </Typography>

                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{
                        mb: 2,
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden',
                      }}
                    >
                      {activity.description}
                    </Typography>

                    <Box display="flex" gap={1}>
                      <Chip
                        icon={<EventIcon />}
                        label={`${activity.event_count || 0} eventos`}
                        size="small"
                        color="primary"
                      />
                      <Chip
                        label={activity.is_active ? 'Activa' : 'Inactiva'}
                        size="small"
                        color={activity.is_active ? 'success' : 'default'}
                      />
                    </Box>
                  </CardContent>

                  <CardActions>
                    <Button
                      size="small"
                      onClick={() => navigate(`/activities/${activity.id}`)}
                    >
                      Ver
                    </Button>
                    <Button
                      size="small"
                      startIcon={<Edit />}
                      onClick={() => navigate(`/teacher/activities/${activity.id}/edit`)}
                    >
                      Editar
                    </Button>
                    <Button
                      size="small"
                      onClick={() => navigate(`/teacher/activities/${activity.id}/events`)}
                    >
                      Gestionar Eventos
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}

        <Dialog
          open={createDialog}
          onClose={() => setCreateDialog(false)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>Crear Nueva Actividad</DialogTitle>
          <DialogContent>
            <TextField
              fullWidth
              label="Título"
              margin="normal"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            />
            <TextField
              fullWidth
              label="Descripción"
              margin="normal"
              multiline
              rows={4}
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            />
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Mínimo de participantes"
                  type="number"
                  margin="normal"
                  value={formData.min_participants_per_meeting}
                  onChange={(e) => setFormData({ ...formData, min_participants_per_meeting: parseInt(e.target.value) })}
                  inputProps={{ min: 2 }}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Máximo de participantes"
                  type="number"
                  margin="normal"
                  value={formData.max_participants_per_meeting}
                  onChange={(e) => setFormData({ ...formData, max_participants_per_meeting: parseInt(e.target.value) })}
                  inputProps={{ min: 2 }}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setCreateDialog(false)}>
              Cancelar
            </Button>
            <Button onClick={handleCreate} variant="contained">
              Crear
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
  );
};

export default MyActivities;

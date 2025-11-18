import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  CircularProgress,
  Alert,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import { activitiesAPI, eventsAPI, enrollmentsAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import {
  AccessTime,
  Event,
  CheckCircle,
  Cancel,
  Person,
  AttachFile,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

const ActivityDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isTeacher } = useAuth();

  const [activity, setActivity] = useState(null);
  const [events, setEvents] = useState([]);
  const [myEnrollments, setMyEnrollments] = useState(new Set());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [enrolling, setEnrolling] = useState(null);

  useEffect(() => {
    loadData();
  }, [id]);

  const loadData = async () => {
    try {
      const [activityRes, eventsRes, enrollmentsRes] = await Promise.all([
        activitiesAPI.getOne(id),
        eventsAPI.getAll({ activity: id }),
        enrollmentsAPI.getMy({ upcoming: true }),
      ]);

      setActivity(activityRes.data);
      setEvents(eventsRes.data.results || eventsRes.data);

      const enrolledEventIds = new Set(
        (enrollmentsRes.data.results || enrollmentsRes.data)
          .filter(e => e.is_active)
          .map(e => e.event)
      );
      setMyEnrollments(enrolledEventIds);
    } catch (err) {
      setError('Error al cargar datos');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleEnroll = async (eventId) => {
    setEnrolling(eventId);
    try {
      await enrollmentsAPI.enroll(eventId);
      setMyEnrollments(prev => new Set([...prev, eventId]));
    } catch (err) {
      alert(err.response?.data?.detail || 'Error al inscribirse');
    } finally {
      setEnrolling(null);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  if (!activity) {
    return (
      <Container>
        <Alert severity="error">Actividad no encontrada</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Button onClick={() => navigate('/activities')} sx={{ mb: 2 }}>
          ← Volver a Actividades
        </Button>

        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h4" gutterBottom>
            {activity.title}
          </Typography>

          <Box display="flex" gap={1} mb={3}>
            <Chip
              icon={<Person />}
              label={`${activity.min_participants_per_meeting}-${activity.max_participants_per_meeting} participantes por grupo`}
              color="primary"
            />
            <Chip
              label={`Por: ${activity.created_by_name}`}
            />
          </Box>

          <Divider sx={{ my: 2 }} />

          <Typography variant="h6" gutterBottom>
            Descripción
          </Typography>
          <Typography variant="body1" paragraph sx={{ whiteSpace: 'pre-line' }}>
            {activity.description}
          </Typography>

          {activity.files && activity.files.length > 0 && (
            <>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom>
                Archivos
              </Typography>
              <List>
                {activity.files.map((file) => (
                  <ListItem key={file.id}>
                    <ListItemIcon>
                      <AttachFile />
                    </ListItemIcon>
                    <ListItemText
                      primary={file.filename}
                      secondary={`${(file.file_size / 1024).toFixed(2)} KB`}
                    />
                    <Button
                      href={file.file}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      Descargar
                    </Button>
                  </ListItem>
                ))}
              </List>
            </>
          )}
        </Paper>

        <Typography variant="h5" sx={{ mt: 4, mb: 2 }}>
          Eventos Disponibles
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {events.length === 0 ? (
          <Alert severity="info">
            No hay eventos programados para esta actividad.
          </Alert>
        ) : (
          <Grid container spacing={2}>
            {events.map((event) => {
              const isEnrolled = myEnrollments.has(event.id);
              const isPast = new Date(event.end_time) < new Date();

              return (
                <Grid item xs={12} md={6} key={event.id}>
                  <Card>
                    <CardContent>
                      <Box display="flex" alignItems="center" mb={1}>
                        <Event sx={{ mr: 1, color: 'primary.main' }} />
                        <Typography variant="h6">
                          {format(new Date(event.start_time), "d 'de' MMMM, yyyy", { locale: es })}
                        </Typography>
                      </Box>

                      <Box display="flex" alignItems="center" mb={2}>
                        <AccessTime sx={{ mr: 1, fontSize: 20 }} />
                        <Typography variant="body2">
                          {format(new Date(event.start_time), 'HH:mm')} - {format(new Date(event.end_time), 'HH:mm')}
                        </Typography>
                      </Box>

                      <Box display="flex" gap={1} mb={2}>
                        <Chip
                          label={`${event.enrolled_count || 0} inscritos`}
                          size="small"
                        />
                        <Chip
                          label={event.status}
                          size="small"
                          color={event.status === 'SCHEDULED' ? 'success' : 'default'}
                        />
                      </Box>

                      {isEnrolled ? (
                        <Button
                          variant="outlined"
                          color="success"
                          startIcon={<CheckCircle />}
                          fullWidth
                          disabled
                        >
                          Ya Inscrito
                        </Button>
                      ) : isPast ? (
                        <Button
                          variant="outlined"
                          disabled
                          fullWidth
                        >
                          Evento Finalizado
                        </Button>
                      ) : (
                        <Button
                          variant="contained"
                          onClick={() => handleEnroll(event.id)}
                          disabled={enrolling === event.id || !event.can_enroll}
                          fullWidth
                        >
                          {enrolling === event.id ? 'Inscribiendo...' : 'Inscribirse'}
                        </Button>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              );
            })}
          </Grid>
        )}
      </Box>
    </Container>
  );
};

export default ActivityDetail;

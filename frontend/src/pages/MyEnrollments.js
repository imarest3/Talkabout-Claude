import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  CardActions,
  Button,
  Grid,
  Chip,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import { enrollmentsAPI, meetingsAPI } from '../services/api';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import { Event, AccessTime, VideoCall, Cancel } from '@mui/icons-material';

const MyEnrollments = () => {
  const [enrollments, setEnrollments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [cancelDialog, setCancelDialog] = useState(null);
  const [meetingUrl, setMeetingUrl] = useState(null);

  useEffect(() => {
    loadEnrollments();
  }, []);

  const loadEnrollments = async () => {
    try {
      const response = await enrollmentsAPI.getMy({ upcoming: true });
      const data = response.data.results || response.data;
      setEnrollments(data.filter(e => e.is_active));
    } catch (err) {
      setError('Error al cargar inscripciones');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async (id) => {
    try {
      await enrollmentsAPI.cancel(id);
      setEnrollments(prev => prev.filter(e => e.id !== id));
      setCancelDialog(null);
    } catch (err) {
      alert(err.response?.data?.detail || 'Error al cancelar inscripción');
    }
  };

  const handleJoinMeeting = async (eventId) => {
    try {
      const response = await meetingsAPI.getAll({ event: eventId });
      const meetings = response.data.results || response.data;

      if (meetings.length > 0) {
        const meeting = meetings[0];
        if (meeting.meeting_url) {
          window.open(meeting.meeting_url, '_blank');
          await meetingsAPI.join(meeting.id);
        } else {
          alert('La reunión aún no está disponible');
        }
      } else {
        alert('La reunión aún no ha sido creada');
      }
    } catch (err) {
      console.error(err);
      alert('Error al acceder a la reunión');
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
          Mis Inscripciones
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {enrollments.length === 0 ? (
          <Alert severity="info">
            No tienes inscripciones activas.
            <Button href="/activities" sx={{ ml: 2 }}>
              Explorar Actividades
            </Button>
          </Alert>
        ) : (
          <Grid container spacing={3} sx={{ mt: 2 }}>
            {enrollments.map((enrollment) => {
              const eventDate = new Date(enrollment.event_start_time);
              const now = new Date();
              const isToday = eventDate.toDateString() === now.toDateString();
              const hasStarted = eventDate <= now;
              const hoursDiff = (eventDate - now) / (1000 * 60 * 60);

              return (
                <Grid item xs={12} md={6} key={enrollment.id}>
                  <Card elevation={3}>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        {enrollment.event_title}
                      </Typography>

                      <Box display="flex" alignItems="center" mb={1}>
                        <Event sx={{ mr: 1, fontSize: 20 }} />
                        <Typography variant="body2">
                          {format(eventDate, "d 'de' MMMM, yyyy", { locale: es })}
                        </Typography>
                      </Box>

                      <Box display="flex" alignItems="center" mb={2}>
                        <AccessTime sx={{ mr: 1, fontSize: 20 }} />
                        <Typography variant="body2">
                          {format(eventDate, 'HH:mm')}
                        </Typography>
                      </Box>

                      {isToday && (
                        <Chip
                          label="Hoy"
                          color="primary"
                          size="small"
                          sx={{ mb: 2 }}
                        />
                      )}

                      {hasStarted && hoursDiff < 1 && (
                        <Alert severity="success" sx={{ mb: 2 }}>
                          ¡La reunión está en curso!
                        </Alert>
                      )}

                      {!hasStarted && hoursDiff <= 24 && (
                        <Alert severity="info" sx={{ mb: 2 }}>
                          Comienza en {Math.round(hoursDiff)} horas
                        </Alert>
                      )}

                      <Typography variant="caption" color="text.secondary">
                        Inscrito el {format(new Date(enrollment.enrolled_at), "d 'de' MMMM", { locale: es })}
                      </Typography>
                    </CardContent>

                    <CardActions>
                      {hasStarted && hoursDiff < 1 ? (
                        <Button
                          variant="contained"
                          startIcon={<VideoCall />}
                          onClick={() => handleJoinMeeting(enrollment.event)}
                          fullWidth
                        >
                          Unirse a la Reunión
                        </Button>
                      ) : (
                        <Button
                          variant="outlined"
                          color="error"
                          startIcon={<Cancel />}
                          onClick={() => setCancelDialog(enrollment)}
                          fullWidth
                        >
                          Cancelar Inscripción
                        </Button>
                      )}
                    </CardActions>
                  </Card>
                </Grid>
              );
            })}
          </Grid>
        )}

        <Dialog
          open={!!cancelDialog}
          onClose={() => setCancelDialog(null)}
        >
          <DialogTitle>Cancelar Inscripción</DialogTitle>
          <DialogContent>
            ¿Estás seguro de que quieres cancelar tu inscripción a "{cancelDialog?.event_title}"?
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setCancelDialog(null)}>
              No, mantener
            </Button>
            <Button
              onClick={() => handleCancel(cancelDialog.id)}
              color="error"
              variant="contained"
            >
              Sí, cancelar
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
  );
};

export default MyEnrollments;

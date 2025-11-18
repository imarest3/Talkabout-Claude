import React from 'react';
import { Container, Typography, Box, Paper, Grid, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  School,
  Event,
  VideoCall,
  Assessment,
} from '@mui/icons-material';

const Home = () => {
  const { user, isTeacher } = useAuth();
  const navigate = useNavigate();

  const features = [
    {
      icon: <School fontSize="large" />,
      title: 'Actividades de Conversación',
      description: 'Participa en actividades grupales para practicar idiomas',
      action: () => navigate('/activities'),
    },
    {
      icon: <Event fontSize="large" />,
      title: 'Eventos Programados',
      description: 'Inscríbete en los horarios que mejor se adapten a ti',
      action: () => navigate('/activities'),
    },
    {
      icon: <VideoCall fontSize="large" />,
      title: 'Videoconferencias',
      description: 'Únete a reuniones virtuales con otros estudiantes',
      action: () => navigate('/my-enrollments'),
    },
    {
      icon: <Assessment fontSize="large" />,
      title: 'Estadísticas',
      description: 'Consulta tu progreso y participación',
      action: () => navigate('/statistics'),
    },
  ];

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom align="center">
          Bienvenido a Talkabout
        </Typography>

        <Typography variant="h6" align="center" color="text.secondary" paragraph>
          {user?.first_name ? `Hola ${user.first_name}!` : 'Hola!'}
          {' '}Plataforma de actividades de conversación para MOOCs
        </Typography>

        {isTeacher && (
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Button
              variant="contained"
              size="large"
              onClick={() => navigate('/my-activities')}
              sx={{ mr: 2 }}
            >
              Gestionar Mis Actividades
            </Button>
            <Button
              variant="outlined"
              size="large"
              onClick={() => navigate('/statistics')}
            >
              Ver Estadísticas
            </Button>
          </Box>
        )}

        <Grid container spacing={4} sx={{ mt: 4 }}>
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Paper
                elevation={3}
                sx={{
                  p: 3,
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  textAlign: 'center',
                  cursor: 'pointer',
                  '&:hover': {
                    elevation: 6,
                    transform: 'translateY(-4px)',
                    transition: 'all 0.3s',
                  },
                }}
                onClick={feature.action}
              >
                <Box sx={{ color: 'primary.main', mb: 2 }}>
                  {feature.icon}
                </Box>
                <Typography variant="h6" gutterBottom>
                  {feature.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {feature.description}
                </Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>

        <Box sx={{ mt: 6, p: 3, bgcolor: 'background.paper', borderRadius: 2 }}>
          <Typography variant="h5" gutterBottom>
            ¿Cómo funciona?
          </Typography>
          <Grid container spacing={2} sx={{ mt: 2 }}>
            <Grid item xs={12} md={4}>
              <Typography variant="h6" color="primary">1. Explora</Typography>
              <Typography variant="body2" color="text.secondary">
                Busca actividades de conversación que te interesen
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="h6" color="primary">2. Inscríbete</Typography>
              <Typography variant="body2" color="text.secondary">
                Selecciona el horario que mejor se adapte a ti
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="h6" color="primary">3. Participa</Typography>
              <Typography variant="body2" color="text.secondary">
                Únete a la videoconferencia y practica con otros estudiantes
              </Typography>
            </Grid>
          </Grid>
        </Box>
      </Box>
    </Container>
  );
};

export default Home;

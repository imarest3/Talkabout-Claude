import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box, IconButton, Menu, MenuItem } from '@mui/material';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { AccountCircle, ExitToApp } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

const Navbar = () => {
  const { user, logout, isTeacher, isAdmin } = useAuth();
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = React.useState(null);

  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component={RouterLink} to="/" sx={{ flexGrow: 1, textDecoration: 'none', color: 'inherit' }}>
          Talkabout
        </Typography>

        {user && (
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <Button color="inherit" component={RouterLink} to="/">
              Inicio
            </Button>

            <Button color="inherit" component={RouterLink} to="/activities">
              Actividades
            </Button>

            {isTeacher && (
              <Button color="inherit" component={RouterLink} to="/my-activities">
                Mis Actividades
              </Button>
            )}

            <Button color="inherit" component={RouterLink} to="/my-enrollments">
              Mis Inscripciones
            </Button>

            {isAdmin && (
              <Button color="inherit" component={RouterLink} to="/admin">
                Admin
              </Button>
            )}

            <IconButton
              size="large"
              onClick={handleMenu}
              color="inherit"
            >
              <AccountCircle />
            </IconButton>
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleClose}
            >
              <MenuItem onClick={() => { handleClose(); navigate('/profile'); }}>
                Perfil
              </MenuItem>
              <MenuItem onClick={() => { handleClose(); navigate('/statistics'); }}>
                Estadísticas
              </MenuItem>
              <MenuItem onClick={handleLogout}>
                <ExitToApp sx={{ mr: 1 }} /> Cerrar Sesión
              </MenuItem>
            </Menu>
          </Box>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;

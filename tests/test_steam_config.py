#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test específico para las nuevas funcionalidades de configuración de Steam v2.1.

Este test valida:
- Detección automática de Steam
- Configuración de rutas personalizadas
- Validación de instalaciones de Steam
- Persistencia de configuración personalizada
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Imports del proyecto
from src.core.steam_config_service import SteamConfigurationService
from src.core.steam_service import SteamAccountService
from src.models.domain_models import AppConfig


class TestSteamConfiguration(unittest.TestCase):
    """Tests para la configuración de Steam"""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.app_config = AppConfig()
        self.steam_config_service = SteamConfigurationService(self.app_config)
    
    def test_validate_steam_path_valid(self):
        """Test validación de ruta de Steam válida."""
        steam_service = SteamAccountService()
        
        # Crear directorio temporal que simule Steam
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear estructura de archivos de Steam
            steam_exe = os.path.join(temp_dir, "steam.exe")
            userdata_dir = os.path.join(temp_dir, "userdata")
            steamapps_dir = os.path.join(temp_dir, "steamapps")
            
            # Crear archivos/directorios
            Path(steam_exe).touch()
            os.makedirs(userdata_dir)
            os.makedirs(steamapps_dir)
            
            # Validar que la ruta se considera válida
            self.assertTrue(steam_service._validate_steam_path(temp_dir))
    
    def test_validate_steam_path_invalid(self):
        """Test validación de ruta de Steam inválida."""
        steam_service = SteamAccountService()
        
        # Directorio vacío no es válido
        with tempfile.TemporaryDirectory() as temp_dir:
            self.assertFalse(steam_service._validate_steam_path(temp_dir))
        
        # Ruta inexistente no es válida
        self.assertFalse(steam_service._validate_steam_path("/ruta/inexistente"))
        
        # Ruta vacía no es válida
        self.assertFalse(steam_service._validate_steam_path(""))
    
    def test_custom_steam_path_configuration(self):
        """Test configuración de ruta personalizada de Steam."""
        steam_service = SteamAccountService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear estructura de Steam válida
            steam_exe = os.path.join(temp_dir, "steam.exe")
            userdata_dir = os.path.join(temp_dir, "userdata")
            steamapps_dir = os.path.join(temp_dir, "steamapps")
            
            Path(steam_exe).touch()
            os.makedirs(userdata_dir)
            os.makedirs(steamapps_dir)
            
            # Configurar ruta personalizada
            result = steam_service.set_custom_steam_path(temp_dir)
            self.assertTrue(result)
            self.assertEqual(steam_service.custom_steam_path, str(Path(temp_dir)))
            self.assertEqual(steam_service.steam_userdata_path, Path(userdata_dir))

    def test_account_without_dota_folder_is_listed(self):
        """Lista una cuenta sin carpeta 570 sin crearla durante la detección."""
        steam_service = SteamAccountService()

        with tempfile.TemporaryDirectory() as temp_dir:
            userdata_path = Path(temp_dir) / "userdata"
            user_path = userdata_path / "123456789"
            user_path.mkdir(parents=True)
            steam_service.steam_userdata_path = userdata_path

            account = steam_service._process_steam_folder("123456789")

            self.assertIsNotNone(account)
            self.assertFalse(account.config_exists)
            self.assertFalse(user_path.joinpath("570").exists())

    def test_copy_creates_dota_folder_and_keeps_remotecache(self):
        """Crea la 570 del destino y conserva su remotecache.vdf propio."""
        from src.core.config_service import FileCopyService

        with tempfile.TemporaryDirectory() as temp_dir:
            origen = Path(temp_dir) / "userdata" / "1" / "570"
            origen.joinpath("local", "cfg").mkdir(parents=True)
            origen.joinpath("local", "cfg", "user_keys_0_slot0.vcfg").write_text("teclas")
            origen.joinpath("remotecache.vdf").write_text("nube origen")

            destino_nuevo = Path(temp_dir) / "userdata" / "2" / "570"
            self.assertTrue(FileCopyService()._copy_folder_recursive(origen, destino_nuevo))
            self.assertEqual(
                destino_nuevo.joinpath("local", "cfg", "user_keys_0_slot0.vcfg").read_text(), "teclas")
            self.assertFalse(destino_nuevo.joinpath("remotecache.vdf").exists())

            destino_existente = Path(temp_dir) / "userdata" / "3" / "570"
            destino_existente.mkdir(parents=True)
            destino_existente.joinpath("remotecache.vdf").write_text("nube destino")
            self.assertTrue(FileCopyService()._copy_folder_recursive(origen, destino_existente))
            self.assertEqual(destino_existente.joinpath("remotecache.vdf").read_text(), "nube destino")

    def test_non_account_userdata_folder_is_ignored(self):
        """No crea carpetas de juego fuera de directorios de cuentas Steam."""
        steam_service = SteamAccountService()

        with tempfile.TemporaryDirectory() as temp_dir:
            userdata_path = Path(temp_dir) / "userdata"
            userdata_path.joinpath("config").mkdir(parents=True)
            steam_service.steam_userdata_path = userdata_path

            self.assertIsNone(steam_service._process_steam_folder("config"))
            self.assertFalse(userdata_path.joinpath("config", "570").exists())
    
    def test_app_config_custom_steam_path(self):
        """Test persistencia de ruta personalizada en AppConfig."""
        # Configurar ruta personalizada
        custom_path = r"C:\Custom\Steam\Path"
        self.app_config.custom_steam_path = custom_path
        
        # Verificar que se almacena correctamente
        self.assertEqual(self.app_config.custom_steam_path, custom_path)
        
        # Crear nuevo servicio con la configuración
        steam_service = SteamAccountService(self.app_config.custom_steam_path)
        self.assertEqual(steam_service.custom_steam_path, custom_path)
    
    @patch('src.core.steam_service.SteamAccountService.get_default_steam_paths')
    def test_auto_detection_with_multiple_paths(self, mock_paths):
        """Test detección automática con múltiples rutas posibles."""
        # Simular múltiples rutas encontradas
        mock_paths.return_value = [
            r"C:\Program Files (x86)\Steam",
            r"D:\Steam"
        ]
        
        # Detectar Steam debería funcionar
        result = self.steam_config_service.detect_steam_installation()
        
        # Como es un mock, el resultado depende de la implementación real
        # Pero al menos verificamos que se llama correctamente
        mock_paths.assert_called_once()
    
    @patch('src.core.steam_service.SteamAccountService.get_default_steam_paths')
    def test_auto_detection_no_steam_found(self, mock_paths):
        """Test detección automática cuando no se encuentra Steam."""
        # Simular que no se encuentra Steam
        mock_paths.return_value = []
        
        # Detectar Steam debería fallar
        result = self.steam_config_service.detect_steam_installation()
        self.assertFalse(result)
    
    def test_get_default_steam_paths(self):
        """Test obtención de rutas predeterminadas de Steam."""
        steam_service = SteamAccountService()
        paths = steam_service.get_default_steam_paths()
        
        # Debe retornar una lista (puede estar vacía si no hay Steam)
        self.assertIsInstance(paths, list)
        
        # Si hay rutas, deben ser strings válidos
        for path in paths:
            self.assertIsInstance(path, str)
            self.assertTrue(len(path) > 0)
    
    def test_steam_userdata_path_with_custom_path(self):
        """Test que la ruta userdata se construye correctamente con ruta personalizada."""
        custom_steam_path = r"C:\Custom\Steam"
        steam_service = SteamAccountService(custom_steam_path)
        
        # Mock de os.path.exists para simular que existe
        with patch('os.path.exists', return_value=True):
            expected_userdata = os.path.join(custom_steam_path, "userdata")
            actual_userdata = steam_service._get_steam_userdata_path()
            self.assertEqual(actual_userdata, Path(expected_userdata))
    
    def test_steam_service_initialization_with_config(self):
        """Test inicialización del servicio Steam con configuración."""
        # Configurar ruta personalizada en AppConfig
        custom_path = r"C:\Test\Steam"
        self.app_config.custom_steam_path = custom_path
        
        # Crear servicio con configuración
        steam_service = SteamAccountService(self.app_config.custom_steam_path)
        
        # Verificar que usa la ruta personalizada
        self.assertEqual(steam_service.custom_steam_path, custom_path)


class TestSteamConfigurationIntegration(unittest.TestCase):
    """Tests de integración para configuración de Steam"""
    
    def test_complete_configuration_flow(self):
        """Test del flujo completo de configuración de Steam."""
        # 1. Crear configuración inicial
        app_config = AppConfig()
        steam_config_service = SteamConfigurationService(app_config)
        
        # 2. Intentar detección automática
        auto_detected = steam_config_service.detect_steam_installation()
        
        # 3. Si no se detecta automáticamente, la aplicación debería permitir configuración manual
        if not auto_detected:
            # Simular configuración manual
            with tempfile.TemporaryDirectory() as temp_dir:
                # Crear estructura de Steam válida
                steam_exe = os.path.join(temp_dir, "steam.exe")
                userdata_dir = os.path.join(temp_dir, "userdata")
                steamapps_dir = os.path.join(temp_dir, "steamapps")
                
                Path(steam_exe).touch()
                os.makedirs(userdata_dir)
                os.makedirs(steamapps_dir)
                
                # Configurar manualmente
                app_config.custom_steam_path = temp_dir
                
                # Reinicializar servicio
                steam_config_service = SteamConfigurationService(app_config)
                
                # Ahora debería detectar Steam
                detected = steam_config_service.detect_steam_installation()
                self.assertTrue(detected)


def run_steam_config_tests():
    """Ejecuta los tests de configuración de Steam."""
    # Crear suite de tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Agregar tests
    suite.addTest(loader.loadTestsFromTestCase(TestSteamConfiguration))
    suite.addTest(loader.loadTestsFromTestCase(TestSteamConfigurationIntegration))
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("=" * 60)
    print("  TESTS DE CONFIGURACIÓN DE STEAM v2.1")
    print("=" * 60)
    
    success = run_steam_config_tests()
    
    print("\\n" + "=" * 60)
    if success:
        print("✅ TODOS LOS TESTS DE CONFIGURACIÓN DE STEAM PASARON")
    else:
        print("❌ ALGUNOS TESTS DE CONFIGURACIÓN DE STEAM FALLARON")
    print("=" * 60)

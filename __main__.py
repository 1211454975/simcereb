# simcereb/__main__.py  
"""  
Main entry point for the SimCereb application  
"""  
  
import sys  
import os  
import argparse  
from PyQt5.QtWidgets import QApplication  
  
from .core.config.config_manager import ConfigManager  
from .core.config.version_manager import VersionManager  
from .core.engine.simulation_engine import SimulationEngine  
from .ui.studio import SimCerebStudio  
  
def main():  
    """Main entry point for the application"""  
    # Parse command line arguments  
    parser = argparse.ArgumentParser(description="SimCereb - 人形机器人小脑系统模拟教育平台")  
    parser.add_argument("--config", help="配置文件路径")  
    parser.add_argument("--version", choices=["learning", "research", "teaching"],   
                        help="版本 (学习版, 研究版, 教学版)")  
    args = parser.parse_args()  
      
    # Create application  
    app = QApplication(sys.argv)  
    app.setApplicationName("SimCereb Studio")  
    app.setOrganizationName("SimCereb")  
      
    # Create configuration manager  
    config_manager = ConfigManager(args.config, args.version)  
      
    # Create version manager  
    version_manager = VersionManager(config_manager)  
      
    # Override version if specified in command line  
    if args.version:  
        version_manager.set_version(args.version)  
      
    # Create simulation engine  
    engine = SimulationEngine(config_manager)  
      
    # Create main window  
    window = SimCerebStudio(engine, config_manager, version_manager)  
    window.show()  
      
    # Run application  
    sys.exit(app.exec_())  
  
if __name__ == "__main__":  
    main()
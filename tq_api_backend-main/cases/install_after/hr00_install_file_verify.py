# -*- coding:utf-8 -*-
import sys
import time

import allure
import pytest
import requests

from apis.center_install_uninstall.data_center_install import DataCenterInstall, DataCenterInstallLinux
from cases.conftest import api
from conf.config import conf
from conf.confpath import ConfPath
from utils.assert_file_reg_process import AssertFileRegProcess
from utils.cmd_line import cmd
from utils.file import File, fo
from utils.log import log
from utils.report import report_show


@allure.epic('安装')
class Hrc1746:
    """ 安装文件验证 """

    def setup_class(self):
        self.afrp = AssertFileRegProcess()
        self.dci = DataCenterInstall()
        self.dci_linux = DataCenterInstallLinux()

    @pytest.mark.skipif(sys.platform not in ('dos', 'win32', 'win16'), reason='linux系统跳过')
    @allure.severity(allure.severity_level.CRITICAL)
    def hr_install_file_verify(self):
        """ 安装文件验证  """
        report_show("安装文件验证", "验证安装目录，注册表以及启动项文件")
        # 验证文件
        self.afrp.assert_files_exist('【断言】 安装目录exe文件存在', self.dci.data_program_escenter_exe_files)
        self.afrp.assert_files_exist('【断言】 安装目录ui文件存在', self.dci.data_program_escenter_ui_files)
        self.afrp.assert_files_exist('【断言】 安装目录dll文件存在', self.dci.data_program_escenter_dll_files)
        self.afrp.assert_files_exist('【断言】 安装目录文件夹存在', self.dci.data_install_dirctory_file_files)
        self.afrp.assert_files_exist('【断言】 安装目录其他文件存在', self.dci.data_program_escenter_other_files)
        self.afrp.assert_files_exist('【断言】 安装目录tools文件夹下的内容', self.dci.data_install_tools_file)
        self.afrp.assert_files_exist('【断言】 安装目录upgrade文件夹下存在的内容', self.dci.data_install_upgrade_file)
        self.afrp.assert_files_exist('【断言】 安装目录wkhtmltopdf文件夹下存在的内容', self.dci.data_install_wkhtmltopdf_file)
        self.afrp.assert_files_exist('【断言】 安装目录package文件夹下存在的内容', self.dci.data_install_package_files)
        self.afrp.assert_files_exist('【断言】 安装目录docs文件夹下内容', self.dci.data_install_docs_files)
        self.afrp.assert_files_exist('【断言】 安装目录deploy文件夹下的内容', self.dci.data_install_deploy_files)

        # 验证活动进程
        self.afrp.assert_process_running('【断言】活动进程的存在', self.dci.data_activity_processing)
        self.afrp.assert_process_startup('【断言】托盘进程在自启动中', self.dci.data_auto_process)

        # 验证系统运行的服务
        self.afrp.assert_service_running('【断言】中心运行的DaemonCenter服务存在', self.dci.data_service_daemoncenter)

        # 验证快捷方式
        self.afrp.assert_files_exist('【断言】 火绒控制中心状态监测工具桌面快捷方式', self.dci.data_desktop_condition_monitoring_lnk)
        self.afrp.assert_files_exist('【断言】 火绒终端安全控制中心桌面快捷方式', self.dci.data_desktop_safty_control_center_lnk)
        self.afrp.assert_files_exist('【断言】 系统开始菜单', self.dci.data_start_menu)

        # 验证系统配置项
        self.afrp.assert_reg_value('【断言】添加软件相关注册表项', self.dci.data_install_file_reg)
        self.afrp.assert_reg_value('【断言】添加托盘自启动相关注册表项', self.dci.data_reg_tray)
        self.afrp.assert_reg_value('【断言】服务信息', self.dci.data_reg_soft)
        self.afrp.assert_reg_value('【断言】添加卸载相关注册表项', self.dci.data_reg_uninstall)
        self.afrp.assert_reg_value('【断言】添加mysql相关注册表项', self.dci.data_reg_mysql)

        # 对比文件内容一致
        File().copy_tree(DataCenterInstall.data_install_config_src, DataCenterInstall.data_desktop_config)
        self.afrp.assert_compare_json_same("【断言】linux_client_v1文件夹中的内容一致", DataCenterInstall.data_install_config_linux_client_v1)
        self.afrp.assert_compare_json_same("【断言】linux_client_v2文件夹中的内容一致", DataCenterInstall.data_install_config_linux_client_v2)
        self.afrp.assert_compare_json_same("【断言】linux_desktop_client_v2文件夹中的内容一致", DataCenterInstall.data_install_config_linux_desktop_client_v2)
        self.afrp.assert_compare_json_same("【断言】linux_server_client_v2文件夹中的内容一致", DataCenterInstall.data_install_config_linux_server_client_v2)
        self.afrp.assert_compare_json_same("【断言】macos_client_v2文件夹中的内容一致", DataCenterInstall.data_install_config_macos_client_v2)
        self.afrp.assert_compare_json_same("【断言】windows_client_v1文件夹中的内容一致", DataCenterInstall.data_install_config_windows_client_v1)
        self.afrp.assert_compare_json_same("【断言】windows_client_v2文件夹中的内容一致", DataCenterInstall.data_install_config_windows_client_v2)
        File().remove_all(DataCenterInstall.data_desktop_config)
        self.afrp.assert_files_exist(f"【断言】{DataCenterInstall.data_desktop_config}文件被删除", DataCenterInstall.data_desktop_config, exist=False)

    @pytest.mark.skipif(sys.platform in ('dos', 'win32', 'win16'), reason='Windows系统跳过')
    @allure.severity(allure.severity_level.CRITICAL)
    def hr_install_file_verify_linux(self):
        """ 安装文件验证  """
        report_show("安装文件验证", "验证安装目录、服务文件")
        # 验证文件
        self.afrp.assert_files_exist('【断言】 安装目录bin文件夹下内容存在', self.dci_linux.data_install_bin_files)
        self.afrp.assert_files_exist('【断言】 安装目录database文件夹下内容存在', self.dci_linux.data_install_database_files)
        self.afrp.assert_files_exist('【断言】 安装目录deploy文件夹下内存存在', self.dci_linux.data_install_deploy_files)
        self.afrp.assert_files_exist('【断言】 安装目录docs文件夹下内容存在', self.dci_linux.data_install_docs_files)
        self.afrp.assert_files_exist('【断言】 安装目录essweb文件夹下内容存在', self.dci_linux.data_install_essweb_files)
        self.afrp.assert_files_exist('【断言】 安装目录i18n文件夹下内容存在', self.dci_linux.data_install_i18n_files)
        self.afrp.assert_files_exist('【断言】 安装目录lib文件夹下内容存在', self.dci_linux.data_install_lib_files)
        self.afrp.assert_files_exist('【断言】 安装目录mysql文件夹下内容存在', self.dci_linux.data_install_mysql_files)
        self.afrp.assert_files_exist('【断言】 安装目录nginx文件夹下内容存在', self.dci_linux.data_install_nginx_files)
        self.afrp.assert_files_exist('【断言】 安装目录package文件夹下内容存在', self.dci_linux.data_install_package_files)
        self.afrp.assert_files_exist('【断言】 安装目录share文件夹下内容存在', self.dci_linux.data_install_share_files)
        self.afrp.assert_files_exist('【断言】 安装目录sysconf文件夹下内容存在', self.dci_linux.data_install_sysconf_files)
        self.afrp.assert_files_exist('【断言】 安装目录tools文件夹下内容存在', self.dci_linux.data_install_tools_files)
        self.afrp.assert_files_exist('【断言】 安装目录upgrade文件夹下内容存在', self.dci_linux.data_install_upgrade_file)
        self.afrp.assert_files_exist('【断言】 安装目录卸载更新及版本文件存在', self.dci_linux.data_program_escenter_files)

        # config文件验证，对比文件内容一致
        File().copy_from(self.dci_linux.data_install_config_src, self.dci_linux.data_install_config_home)
        self.afrp.assert_compare_json_same("【断言】linux_client_v1文件夹中的内容一致", self.dci_linux.data_install_config_linux_client_v1)
        self.afrp.assert_compare_json_same("【断言】linux_client_v2文件夹中的内容一致", self.dci_linux.data_install_config_linux_client_v2)
        self.afrp.assert_compare_json_same("【断言】linux_desktop_client_v2文件夹中的内容一致", self.dci_linux.data_install_config_linux_desktop_client_v2)
        self.afrp.assert_compare_json_same("【断言】linux_server_client_v2文件夹中的内容一致", self.dci_linux.data_install_config_linux_server_client_v2)
        self.afrp.assert_compare_json_same("【断言】macos_client_v2文件夹中的内容一致", self.dci_linux.data_install_config_macos_client_v2)
        self.afrp.assert_compare_json_same("【断言】windows_client_v1文件夹中的内容一致", self.dci_linux.data_install_config_windows_client_v1)
        self.afrp.assert_compare_json_same("【断言】windows_client_v2文件夹中的内容一致", self.dci_linux.data_install_config_windows_client_v2)
        File().remove_all(self.dci_linux.data_install_config_path)
        self.afrp.assert_files_exist(f"【断言】{self.dci_linux.data_install_config_path}文件被删除", self.dci_linux.data_install_config_path, exist=False)

        # 服务文件
        self.afrp.assert_files_exist('【断言】 服务文件hresscenter.service存在', self.dci_linux.data_system_hresscenter_service)
        self.afrp.assert_files_exist('【断言】 服务文件软链接hresscenter.service存在', self.dci_linux.data_system_hresscenter_service_multi)

        cmd.assert_process_running_linux('【断言】 正在运行的进程DaemonCenter存在', 'DaemonCenter')
        cmd.assert_process_running_linux('【断言】 正在运行的进程HipsCenter存在', 'HipsCenter')
        cmd.assert_process_running_linux('【断言】 正在运行的进程mysqld存在', 'mysqld')

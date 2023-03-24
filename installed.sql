
create table if not exists otherdata (
    workstation varchar(20),
    inquiry varchar(200),
    result varchar(2000),
    first_seen datetime default current_timestamp,
    packname varchar(20),
    major varchar(20),
    minor varchar(20),
    primary key (workstation, result)
    );
create table if not exists installed (
    workstation varchar(20),
    package_name varchar(200),
    first_seen datetime default current_timestamp,
    primary key (workstation, package_name)
    );
CREATE VIEW has_gpu AS SELECT workstation FROM otherdata WHERE inquiry = 'gpu_driver' AND result != 'None';

CREATE OR REPLACE VIEW when_kernel_changed AS SELECT workstation, first_seen FROM otherdata WHERE inquiry = 'linux_after_reboot';

CREATE OR REPLACE VIEW which_linux_version AS SELECT workstation, result FROM otherdata WHERE inquiry = 'redhat_os';

CREATE OR REPLACE VIEW is_pkg_installed AS SELECT workstation, package_name FROM installed;

CREATE OR REPLACE VIEW pkg_not_installed AS SELECT DISTINCT workstation FROM installed WHERE workstation NOT IN is_pkg_installed;

CREATE OR REPLACE VIEW when_db_last_updated

CREATE OR REPLACE VIEW workstation_last_updated

CREATE OR REPLACE VIEW workstations_updated_lastweek

CREATE OR REPLACE VIEW workstations_outdated_pkgs AS SELECT workstation, package_name FROM installed;

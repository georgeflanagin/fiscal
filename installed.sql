
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
CREATE OR REPLACE VIEW has_gpu AS SELECT workstation FROM otherdata WHERE inquiry = 'gpu_driver' AND result != 'None';

/* select first_seen from when_kernel_changed where workstation = {} ORDER BY first_seen DESC LIMIT 1 */
CREATE OR REPLACE VIEW when_kernel_changed AS SELECT workstation, first_seen FROM otherdata WHERE inquiry = 'linux_after_reboot';

/* select result from which_linux_version where workstation = {} ORDER BY first_seen DESC LIMIT 1 */
CREATE OR REPLACE VIEW which_linux_version AS SELECT workstation, result FROM otherdata WHERE inquiry = 'redhat_os';

/* run select workstation from is_pkg_installed where package_name = {}  */
CREATE OR REPLACE VIEW is_pkg_installed AS SELECT workstation, package_name FROM installed;

CREATE OR REPLACE VIEW pkg_not_installed AS SELECT DISTINCT workstation FROM installed WHERE workstation NOT IN is_pkg_installed;

/* run select max(first_seen) from when_db_last_updated to retrieve the most recent date*/
CREATE OR REPLACE VIEW when_db_last_updated AS SELECT installed.first_seen FROM installed UNION SELECT otherdata.first_seen FROM otherdata; 

/* run select max(first_seen) from workstation_last_updated where workstation = {} to retrieve the date workstation was last updated */
CREATE OR REPLACE VIEW workstation_last_updated AS SELECT installed.workstation, installed.first_seen FROM installed UNION SELECT otherdata.workstation, otherdata.first_seen from otherdata;

/* run select distinct workstation from workstation_last_updated WHERE first_seen>=date() - 7; to find workstations updated in the last week*/
/* CREATE OR REPLACE VIEW workstations_updated_lastweek */

/* select workstation, package_name from workstations_outdated_pkgs WHERE package_name GLOB '{}* */
CREATE OR REPLACE VIEW workstations_outdated_pkgs AS SELECT workstation, package_name FROM installed;




CREATE OR REPLACE VIEW v_packages AS SELECT workstation, package_name FROM installed;

CREATE OR REPLACE VIEW v_updated AS SELECT installed.workstation, installed.first_seen FROM installed UNION SELECT otherdata.workstation, otherdata.first_seen FROM otherdata;

CREATE OR REPLACE VIEW v_gpu AS SELECT workstation, result, first_seen FROM otherdata WHERE inquiry = 'gpu_driver' AND result != 'None';

CREATE OR REPLACE VIEW v_kernel AS SELECT workstation, first_seen, result FROM otherdata WHERE inquiry = 'linux_after_reboot';

CREATE OR REPLACE VIEW v_linux AS SELECT workstation, result FROM otherdata WHERE inquiry = 'redhat_os';

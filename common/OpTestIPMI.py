#!/usr/bin/python
# IBM_PROLOG_BEGIN_TAG
# This is an automatically generated prolog.
#
# $Source: op-auto-test/common/OpTestIPMI.py $
#
# OpenPOWER Automated Test Project
#
# Contributors Listed Below - COPYRIGHT 2015
# [+] International Business Machines Corp.
#
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the License for the specific language governing
# permissions and limitations under the License.
#
# IBM_PROLOG_END_TAG

## @package OpTestIPMI
#  IPMI package which contains all BMC related IPMI commands
#
#  This class encapsulates all function which deals with the BMC over IPMI
#  in OpenPower systems

import time
import subprocess
import os
import pexpect
#from subprocess import check_output
from OpTestConstants import OpTestConstants as BMC_CONST
from OpTestError import OpTestError
from OpTestLpar import OpTestLpar
from OpTestUtil import OpTestUtil

class OpTestIPMI():

    ##
    # @brief Initialize this object
    #
    # @param i_bmcIP @type string: IP Address of the BMC
    # @param i_bmcUser @type string: Userid to log into the BMC
    # @param i_bmcPwd @type string: Password of the userid to log into the BMC
    # @param i_ffdcDir @type string: Optional param to indicate where to write FFDC
    #
    def __init__(self, i_bmcIP, i_bmcUser, i_bmcPwd, i_ffdcDir):

        self.cv_bmcIP = i_bmcIP
        self.cv_bmcUser = i_bmcUser
        self.cv_bmcPwd = i_bmcPwd
        self.cv_ffdcDir = i_ffdcDir
        self.cv_cmd = 'ipmitool -H %s -I lanplus -U %s -P %s ' \
                      % (self.cv_bmcIP, self.cv_bmcUser, self.cv_bmcPwd)
        self.util = OpTestUtil()
        # apss response data address list
        self.ResponseDict = {
                            '0x00' : 'NO_CHANGE' ,       
                            '0x01' : 'REV_CODE'  ,
                            '0x02' : 'DAC0'      ,         
                            '0x03' : 'DAC1'      ,      
                            '0x04' : 'DAC2'      ,         
                            '0x05' : 'DAC3'      ,         
                            '0x06' : 'DAC4'      ,         
                            '0x07' : 'DAC5'      ,         
                            '0x08' : 'DAC6'      ,         
                            '0x09' : 'DAC7'      ,         
                            '0x0a' : 'NO_COMMAND',         
                            '0x0b' : 'NO_COMMAND',         
                            '0x0c' : 'NO_COMMAND',         
                            '0x0d' : 'NO_COMMAND',         
                            '0x0e' : 'NO_COMMAND',         
                            '0x0f' : 'NO_COMMAND',         
                            '0x10' : 'NO_COMMAND',         
                            '0x11' : 'NO_COMMAND',         
                            '0x12' : 'NO_COMMAND',         
                            '0x13' : 'NO_COMMAND',         
                            '0x14' : 'ADC_CH0_LSB',       
                            '0x15' : 'ADC_CH0_MSB',        
                            '0x16' : 'ADC_CH1_LSB',        
                            '0x17' : 'ADC_CH1_MSB',        
                            '0x18' : 'ADC_CH2_LSB',        
                            '0x19' : 'ADC_CH2_MSB',        
                            '0x1a' : 'ADC_CH3_LSB',        
                            '0x1b' : 'ADC_CH3_MSB',        
                            '0x1c' : 'ADC_CH4_LSB',        
                            '0x1d' : 'ADC_CH4_MSB',        
                            '0x1e' : 'ADC_CH5_LSB',        
                            '0x1f' : 'ADC_CH5_MSB',        
                            '0x20' : 'ADC_CH6_LSB',        
                            '0x21' : 'ADC_CH6_MSB',        
                            '0x22' : 'ADC_CH7_LSB',        
                            '0x23' : 'ADC_CH7_MSB',        
                            '0x24' : 'ADC_CH8_LSB',        
                            '0x25' : 'ADC_CH8_MSB',        
                            '0x26' : 'ADC_CH9_LSB',        
                            '0x27' : 'ADC_CH9_MSB',        
                            '0x28' : 'ADC_CH10_LSB',       
                            '0x29' : 'ADC_CH10_MSB',       
                            '0x2a' : 'ADC_CH11_LSB',       
                            '0x2b' : 'ADC_CH11_MSB',       
                            '0x2c' : 'ADC_CH12_LSB',       
                            '0x2d' : 'ADC_CH12_MSB',       
                            '0x2e' : 'ADC_CH13_LSB',       
                            '0x2f' : 'ADC_CH13_MSB',       
                            '0x30' : 'ADC_CH14_LSB',       
                            '0x31' : 'ADC_CH14_MSB',       
                            '0x32' : 'ADC_CH15_LSB',       
                            '0x33' : 'ADC_CH15_MSB',        
                            '0x34' : 'GPIO_IN0'    ,        
                            '0x35' : 'GPIO_IN1'    ,        
                            '0x36' : 'GPIO_MODE0'  ,        
                            '0x37' : 'GPIO_MODE1'  ,        
                            '0x38' : 'GPIO_READONLY',       
                            '0x39' : 'INVALID_CMD',         
                            '0x3a' : 'INVALID_CMD'
        }


    ##
    # @brief Runs an ipmitool command.
    #    The command argument is the last ipmitool command argument, for example:
    #    'chassis power cycle' or 'sdr elist'.  You can append other shell commands
    #    to the string, for instance 'sdr elist|grep Host'.
    #    Use backround=1, to spawn the child process and return the popen object,
    #    rather than waiting for the command completion and returning only the
    #    output.
    #
    # @param cmd @type string: The ipmitool command, for example: chassis power on
    # @param background @type bool: Spawn the command in as a background process.
    #        This is useful to monitor sensors or other runtime info. With
    #        background=False the function will block until the command finishes.
    #
    # @returns When background=1 it returns the subprocess child object. When
    #        background==False,it returns the output of the command.
    #
    #        raises: OpTestError when fails
    #
    def _ipmitool_cmd_run(self, cmd, background=False):

        print cmd
        if background:
            try:
                child = subprocess.Popen(cmd, shell=True)
            except:
                l_msg = "Ipmitool Command Failed"
                print l_msg
                raise OpTestError(l_msg)
            return child
        else:
            # TODO - need python 2.7
            # output = check_output(cmd, stderr=subprocess.STDOUT, shell=True)
            try:
                cmd = subprocess.Popen(cmd,stderr=subprocess.STDOUT,
                                       stdout=subprocess.PIPE,shell=True)
            except:
                l_msg = "Ipmitool Command Failed"
                print l_msg
                raise OpTestError(l_msg)
            output = cmd.communicate()[0]
            return output


    ##
    # @brief This function clears the system event log
    #
    # @return BMC_CONST.FW_SUCCESS or raise OpTestError
    #
    def ipmi_sel_clear(self):

        output = self._ipmitool_cmd_run(self.cv_cmd + 'sel clear')
        if 'Clearing SEL' in output:
            time.sleep(3)
            output = self._ipmitool_cmd_run(self.cv_cmd + 'sel elist')
            if 'no entries' in output:
                return BMC_CONST.FW_SUCCESS
            else:
                l_msg = "Sensor event log still has entries!"
                print l_msg
                raise OpTestError(l_msg)
        else:
            l_msg = "Clearing the system event log Failed"
            print l_msg
            raise OpTestError(l_msg)


    ##
    # @brief This function sends the chassis power off ipmitool command
    #
    # @return BMC_CONST.FW_SUCCESS or raise OpTestError
    #
    def ipmi_power_off(self):
        output = self._ipmitool_cmd_run(self.cv_cmd + 'chassis power off')
        if 'Down/Off' in output:
            return BMC_CONST.FW_SUCCESS
        else:
            l_msg = "Power OFF Failed"
            print l_msg
            raise OpTestError(l_msg)


    ##
    # @brief This function sends the chassis power on ipmitool command
    #
    # @return BMC_CONST.FW_SUCCESS or raise OpTestError
    #
    def ipmi_power_on(self):
        output = self._ipmitool_cmd_run(self.cv_cmd + 'chassis power on')
        if 'Up/On' in output:
            return BMC_CONST.FW_SUCCESS
        else:
            l_msg = "Power ON Failed"
            print l_msg
            raise OpTestError(l_msg)


    ##
    # @brief This function sends the chassis power soft ipmitool command
    #
    # @return BMC_CONST.FW_SUCCESS or raise OpTestError
    #
    def ipmi_power_soft(self):
        output = self._ipmitool_cmd_run(self.cv_cmd + 'chassis power soft')
        if "Chassis Power Control: Soft" in output:
            return BMC_CONST.FW_SUCCESS
        else:
            l_msg = "Power Soft Failed"
            print l_msg
            raise OpTestError(l_msg)


    ##
    # @brief Spawns the sol logger expect script as a background process. In order to
    #        properly kill the process the caller should call the ipmitool sol
    #        deactivate command, i.e.: ipmitool_cmd_run('sol deactivate'). The sol.log
    #        file is placed in the FFDC directory
    #
    # @return OpTestError
    #
    def _ipmi_sol_capture(self):

        try:
            self._ipmitool_cmd_run(self.cv_cmd + 'sol deactivate')
        except OpTestError:
            print 'SOL already deactivated'
        time.sleep(2)
        logFile = self.cv_ffdcDir + '/' + 'host_sol.log'
        cmd = os.getcwd() + '/../common/sol_logger.exp %s %s %s %s' % (
            self.cv_bmcIP,
            self.cv_bmcUser,
            self.cv_bmcPwd,
            logFile)
        print cmd
        try:
            solChild = subprocess.Popen(cmd, shell=True)
        except:
            raise OpTestError("sol capture Failed")
        return solChild


    ##
    # @brief This function starts the sol capture and waits for the IPL to end. The
    #        marker for IPL completion is the Host Status sensor which reflects the ACPI
    #        power state of the system.  When it reads S0/G0: working it means that the
    #        petitboot is has began loading.  The overall timeout for the IPL is defined
    #        in the test configuration options.'''
    #
    # @param timeout @type int: The number of minutes to wait for IPL to complete,
    #       i.e. How long to poll the ACPI sensor for working state before giving up.
    #
    # @return BMC_CONST.FW_SUCCESS or raise OpTestError
    #
    def ipl_wait_for_working_state(self, timeout=10):

        ''' WORKAROUND FOR AMI BUG
         A sleep is required here because Host status sensor is set incorrectly
         to working state right after power on '''
        sol = self._ipmi_sol_capture()
        time.sleep(60)

        timeout = time.time() + 60*timeout

        ''' AMI BUG is fixed now
         After updating the AMI level the Host Status sensor works as expected.
        '''
        cmd = 'sdr elist |grep \'Host Status\''
        while True:
            output = self._ipmitool_cmd_run(self.cv_cmd + cmd)
            if 'S0/G0: working' in output:
                print "Host Status is S0/G0: working, IPL finished"
                break
            if time.time() > timeout:
                l_msg = "IPL timeout"
                print l_msg
                raise OpTestError(l_msg)
            time.sleep(5)

        try:
            self._ipmitool_cmd_run(self.cv_cmd + 'sol deactivate')
        except subprocess.CalledProcessError:
            l_msg = 'SOL already deactivated'
            print l_msg
            raise OpTestError(l_msg)

        return BMC_CONST.FW_SUCCESS


    ##
    # @brief This function dumps the sel log and looks for specific hostboot error
    #        log string
    #
    # @return BMC_CONST.FW_SUCCESS or raise OpTestError
    #
    def ipmi_sel_check(self,i_string):

        selDesc = 'Transition to Non-recoverable'
        logFile = self.cv_ffdcDir + '/' + 'host_sol.log'
        output = self._ipmitool_cmd_run(self.cv_cmd + 'sel elist')

        with open('%s' % logFile, 'w') as f:
            for line in output:
                f.write(line)

        if i_string in output:
            l_msg = 'Error log(s) detected during IPL. Please see %s' % logFile
            print l_msg
            raise OpTestError(l_msg)
        else:
            return BMC_CONST.FW_SUCCESS

    ##
    # @brief This function get data from apss through i2c bus by using ipmitool and
    #        store the result to apss log.
    #
    # @the response data format is as following:
    # const void * G_i2cResponseDataPtrs[256] = 
    # {
    #     /*  [00]: NO_CHANGE           */ &G_i2cInvalid,
    #     /*  [01]: REV_CODE            */ &G_apssSoftwareRev,
    #     /*  [02]: DAC0                */ &G_pwmChan[0],
    #     /*  [03]: DAC1                */ &G_pwmChan[1],
    #     /*  [04]: DAC2                */ &G_pwmChan[2],
    #     /*  [05]: DAC3                */ &G_pwmChan[3],
    #     /*  [06]: DAC4                */ &G_pwmChan[4],
    #     /*  [07]: DAC5                */ &G_pwmChan[5],
    #     /*  [08]: DAC6                */ &G_pwmChan[6],
    #     /*  [09]: DAC7                */ &G_pwmChan[7],
    #     /*  [0a]: NO_COMMAND          */ &G_i2cInvalid,
    #     /*  [0b]: NO_COMMAND          */ &G_i2cInvalid,
    #     /*  [0c]: NO_COMMAND          */ &G_i2cInvalid,
    #     /*  [0d]: NO_COMMAND          */ &G_i2cInvalid,
    #     /*  [0e]: NO_COMMAND          */ &G_i2cInvalid,
    #     /*  [0f]: NO_COMMAND          */ &G_i2cInvalid,
    #     /*  [10]: NO_COMMAND          */ &G_i2cInvalid,
    #     /*  [11]: NO_COMMAND          */ &G_i2cInvalid,
    #     /*  [12]: NO_COMMAND          */ &G_i2cInvalid,
    #     /*  [13]: NO_COMMAND          */ &G_i2cInvalid,
    #     /*  [14]: ADC_CH0_LSB         */ (uint8_t *) &G_adcChan[0],
    #     /*  [15]: ADC_CH0_MSB         */ &G_i2cInvalid,
    #     /*  [16]: ADC_CH1_LSB         */ (uint8_t *) &G_adcChan[1],
    #     /*  [17]: ADC_CH1_MSB         */ &G_i2cInvalid,
    #     /*  [18]: ADC_CH2_LSB         */ (uint8_t *) &G_adcChan[2],
    #     /*  [19]: ADC_CH2_MSB         */ &G_i2cInvalid,
    #     /*  [1a]: ADC_CH3_LSB         */ (uint8_t *) &G_adcChan[3],
    #     /*  [1b]: ADC_CH3_MSB         */ &G_i2cInvalid,
    #     /*  [1c]: ADC_CH4_LSB         */ (uint8_t *) &G_adcChan[4],
    #     /*  [1d]: ADC_CH4_MSB         */ &G_i2cInvalid,
    #     /*  [1e]: ADC_CH5_LSB         */ (uint8_t *) &G_adcChan[5],
    #     /*  [1f]: ADC_CH5_MSB         */ &G_i2cInvalid,
    #     /*  [20]: ADC_CH6_LSB         */ (uint8_t *) &G_adcChan[6],
    #     /*  [21]: ADC_CH6_MSB         */ &G_i2cInvalid,
    #     /*  [22]: ADC_CH7_LSB         */ (uint8_t *) &G_adcChan[7],
    #     /*  [23]: ADC_CH7_MSB         */ &G_i2cInvalid,
    #     /*  [24]: ADC_CH8_LSB         */ (uint8_t *) &G_adcChan[8],
    #     /*  [25]: ADC_CH8_MSB         */ &G_i2cInvalid,
    #     /*  [26]: ADC_CH9_LSB         */ (uint8_t *) &G_adcChan[9],
    #     /*  [27]: ADC_CH9_MSB         */ &G_i2cInvalid,
    #     /*  [28]: ADC_CH10_LSB        */ (uint8_t *) &G_adcChan[10],
    #     /*  [29]: ADC_CH10_MSB        */ &G_i2cInvalid,
    #     /*  [2a]: ADC_CH11_LSB        */ (uint8_t *) &G_adcChan[11],
    #     /*  [2b]: ADC_CH11_MSB        */ &G_i2cInvalid,
    #     /*  [2c]: ADC_CH12_LSB        */ (uint8_t *) &G_adcChan[12],
    #     /*  [2d]: ADC_CH12_MSB        */ &G_i2cInvalid,
    #     /*  [2e]: ADC_CH13_LSB        */ (uint8_t *) &G_adcChan[13],
    #     /*  [2f]: ADC_CH13_MSB        */ &G_i2cInvalid,
    #     /*  [30]: ADC_CH14_LSB        */ (uint8_t *) &G_adcChan[14],
    #     /*  [31]: ADC_CH14_MSB        */ &G_i2cInvalid,
    #     /*  [32]: ADC_CH15_LSB        */ (uint8_t *) &G_adcChan[15],
    #     /*  [33]: ADC_CH15_MSB        */ &G_i2cInvalid,
    #     /*  [34]: GPIO_IN0            */ &G_gpioPort[0],
    #     /*  [35]: GPIO_IN1            */ &G_gpioPort[1],
    #     /*  [36]: GPIO_MODE0          */ &G_gpioIoConfig[0],
    #     /*  [37]: GPIO_MODE1          */ &G_gpioIoConfig[1],
    #     /*  [38]: GPIO_READONLY       */ &G_softOcPins,
    #     /*  [39]: INVALID_CMD         */ &G_i2cInvalid,
    #     /*  [3a]: INVALID_CMD         */ &G_i2cInvalid,
    # };
    #
    # @return BMC_CONST.FW_SUCCESS or raise OpTestError
    #
    def ipmi_apss_get(self):

        selDesc = 'Transition to Non-recoverable'
        l_cmd = BMC_CONST.BMC_APSS_DATA
        logFile = self.cv_ffdcDir + '/' + 'host_apss.log'
        apssdata = ''
        apssdatalen = len(self.ResponseDict)
        for key in range(apssdatalen):
            addr = '0x%02x'%(key)
            output = self._ipmitool_cmd_run(self.cv_cmd + l_cmd + addr)
            if "nable to send" in output:
                print output
                raise OpTestError(output)
            apssdata = apssdata + '|%10s\t|%10s\t|\t0x%02x\t|\r\n'%(addr,self.ResponseDict[addr],int(output,16))

        apssdata = '|%10s\t|%10s\t|%10s\t|\r\n'%('Address', 'Description', 'Value') + '-'*50 + '\r\n' + apssdata

        with open('%s' % logFile, 'w') as f:
            for line in apssdata:
                f.write(line)


    ##
    # @brief This function used to get the sensor data and store the result to sdr log
    #
    # @return BMC_CONST.FW_SUCCESS or raise OpTestError
    #
    def ipmi_sdr_get(self):

        output = self._ipmitool_cmd_run(self.cv_cmd + 'sdr list')
        logFile = self.cv_ffdcDir + '/' + 'host_sdr.log'
        if "Unable to" in output:
            l_msg = "Getting sensor data record Failed"
            print l_msg
            raise OpTestError(l_msg)
        else:
            with open('%s' % logFile, 'w') as f:
                for line in output:
                    f.write(line)



    ##
    # @brief Performs a cold reset onto the bmc
    #
    # @return BMC_CONST.FW_SUCCESS or raise OpTestError
    #
    def ipmi_cold_reset(self):

        l_cmd = BMC_CONST.BMC_COLD_RESET
        print ("Applying Cold reset. Wait for "
                            + str(BMC_CONST.BMC_COLD_RESET_DELAY) + "sec")
        rc = self._ipmitool_cmd_run(self.cv_cmd + l_cmd)
        if BMC_CONST.BMC_PASS_COLD_RESET in rc:
            print rc
            time.sleep(BMC_CONST.BMC_COLD_RESET_DELAY)
            return BMC_CONST.FW_SUCCESS
        else:
            l_msg = "Cold reset Failed"
            print l_msg
            raise OpTestError(l_msg)


    ##
    # @brief Performs a warm reset onto the bmc
    #
    # @return BMC_CONST.FW_SUCCESS or raise OpTestError
    #
    def ipmi_warm_reset(self):

        l_cmd = BMC_CONST.BMC_WARM_RESET
        print ("Applying Warm reset. Wait for "
                            + str(BMC_CONST.BMC_WARM_RESET_DELAY) + "sec")
        rc = self._ipmitool_cmd_run(self.cv_cmd + l_cmd)
        if BMC_CONST.BMC_PASS_WARM_RESET in rc:
            print rc
            time.sleep(BMC_CONST.BMC_WARM_RESET_DELAY)
            return BMC_CONST.FW_SUCCESS
        else:
            l_msg = "Warm reset Failed"
            print l_msg
            raise OpTestError(l_msg)


    ##
    # @brief Preserves the network setting
    #
    # @return BMC_CONST.FW_SUCCESS or raise OpTestError
    #
    def ipmi_preserve_network_setting(self):

        print ("Protecting BMC network setting")
        l_cmd =  BMC_CONST.BMC_PRESRV_LAN
        rc = self._ipmitool_cmd_run(self.cv_cmd + l_cmd)

        if BMC_CONST.BMC_ERROR_LAN in rc:
            l_msg = "Can't protect setting! Please preserve setting manually"
            print l_msg
            raise OpTestError(l_msg)

        return BMC_CONST.FW_SUCCESS


    ##
    # @brief Flashes image using ipmitool
    #
    # @param i_image @type string: hpm file including location
    # @param i_imagecomponent @type string: component to be
    #        update from the hpm file BMC_CONST.BMC_FW_IMAGE_UPDATE
    #        or BMC_CONST.BMC_PNOR_IMAGE
    #
    # @return BMC_CONST.FW_SUCCESS or raise OpTestError
    #
    def ipmi_code_update(self, i_image, i_imagecomponent):

        self.ipmi_cold_reset()
        l_cmd = BMC_CONST.BMC_HPM_UPDATE + i_image + " " + i_imagecomponent
        self.ipmi_preserve_network_setting()
        try:
            rc = self._ipmitool_cmd_run("echo y | " + self.cv_cmd + l_cmd)
            print rc
            self.ipmi_cold_reset()

        except subprocess.CalledProcessError:
            l_msg = "Code Update Failed"
            print l_msg
            raise OpTestError(l_msg)

        if(rc.__contains__("Firmware upgrade procedure successful")):
            return BMC_CONST.FW_SUCCESS
        else:
            l_msg = "Code Update Failed"
            print l_msg
            raise OpTestError(l_msg)

    ##
    # @brief Verify Primary side activated for both BMC and PNOR
    # example 0x0080 indicates primary side is activated
    #         0x0180 indicates golden side is activated
    #
    # @return prints and returns BMC_CONST.PRIMARY_SIDE
    #         or BMC_CONST.GOLDEN_SIDE or raise OpTestError
    #
    def ipmi_get_side_activated(self):

        rc = self._ipmitool_cmd_run(self.cv_cmd + BMC_CONST.BMC_ACTIVE_SIDE)
        if(rc.__contains__(BMC_CONST.PRIMARY_SIDE)):
            print("Primary side is active")
            return BMC_CONST.PRIMARY_SIDE
        elif(BMC_CONST.GOLDEN_SIDE in rc):
            print ("Golden side is active")
            return BMC_CONST.GOLDEN_SIDE
        else:
            l_msg = "Error determining active side"
            print l_msg
            raise OpTestError(l_msg)

    ##
    # @brief Get PNOR level
    #
    # @return pnor level of the bmc
    #         or raise OpTestError
    #
    def ipmi_get_PNOR_level(self):
        l_rc =  self._ipmitool_cmd_run(self.cv_cmd + BMC_CONST.BMC_MCHBLD)
        print l_rc
        return l_rc

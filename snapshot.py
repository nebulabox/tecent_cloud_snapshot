#!/usr/bin/python3
# -*-coding:UTF-8-*-
"""
腾讯云轻量云自动快照备份
腾讯云API库安装
pip install -i https://mirrors.tencent.com/pypi/simple/ --upgrade tencentcloud-sdk-python
腾讯云账号ID获取地址
https://console.cloud.tencent.com/cam/capi
实例地域
"ap-beijing", "ap-chengdu", "ap-guangzhou", "ap-hongkong", "ap-nanjing", "ap-shanghai", "ap-singapore", "ap-tokyo", "eu-moscow", "na-siliconvalley"
"""
import json
import os
import time
import pytz
from datetime import datetime
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.lighthouse.v20200324 import lighthouse_client, models

SecretId = "xxxxx"
SecretKey = "xxxx"
region = "ap-shanghai"
InstanceIds = "xxxx"

def CreateInstanceSnapshot(SecretId, SecretKey, region, InstanceIds):
    """
    创建快照
    """
    try:
        cred = credential.Credential(SecretId, SecretKey)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "lighthouse.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = lighthouse_client.LighthouseClient(cred, region, clientProfile)
        req = models.CreateInstanceSnapshotRequest()
        params = {
            "InstanceId": InstanceIds
        }
        req.from_json_string(json.dumps(params))
        resp = client.CreateInstanceSnapshot(req)
        resp_re = json.loads(resp.to_json_string())
        SnapshotId = resp_re['SnapshotId']
        print('轻量云快照备份完成，快照ID为：{0},程序5秒钟后关闭'.format(SnapshotId))
        time.sleep(5)
        exit()
    except TencentCloudSDKException as err:
        print(err)
        return False


def DeleteSnapshots(SecretId, SecretKey, SnapshotId, region):
    """
    删除快照
    """
    try:
        cred = credential.Credential(SecretId, SecretKey)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "lighthouse.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = lighthouse_client.LighthouseClient(cred, region, clientProfile)
        req = models.DeleteSnapshotsRequest()
        params = {
            "SnapshotIds": [SnapshotId]
        }
        req.from_json_string(json.dumps(params))
        resp = client.DeleteSnapshots(req)
        return json.loads(resp.to_json_string())
    except TencentCloudSDKException as err:
        print(err)
        return False


def get_info(SecretId, SecretKey, region, InstanceIds):
    try:
        cred = credential.Credential(SecretId, SecretKey)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "lighthouse.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = lighthouse_client.LighthouseClient(cred, region, clientProfile)
        req = models.DescribeSnapshotsRequest()
        params = {
        }
        req.from_json_string(json.dumps(params))
        resp = client.DescribeSnapshots(req)
        return json.loads((resp.to_json_string()))
    except TencentCloudSDKException as err:
        print(err)
        return False

if __name__ == '__main__':
    nowtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print('---------' + str(nowtime) + ' 程序开始执行------------')
    get_rest = get_info(SecretId, SecretKey, region, InstanceIds)
    if get_rest != False:
        TotalCount = get_rest['TotalCount'] # 快照数
        if TotalCount < 2: # 直接备份
            CreateInstanceSnapshot(SecretId, SecretKey, region, InstanceIds)
        elif TotalCount == 2:
            # 删除一个备份。该脚本每天执行一次。
            # 最旧的快照(索引为1)如果超过3天，删除这个。否则删除最新的快照。
            oldcreate=get_rest['SnapshotSet'][1]['CreatedTime'] # '2022-09-02T07:27:23Z'
            olddt=datetime.strptime(oldcreate, '%Y-%m-%dT%H:%M:%SZ') # UTC
            olddt=pytz.utc.localize(olddt)
            utc_now = pytz.utc.localize(datetime.utcnow())
            diff=utc_now-olddt
            delpos=0 # 最新的一个
            if diff.days >= 3 :
                print('删除3天前的备份')
                delpos=1 # 删除最久的一个
            else : 
                print('删除最近的备份')
            SnapshotState = (get_rest['SnapshotSet'][delpos]['SnapshotState'])
            if SnapshotState == 'NORMAL':
                SnapshotId = (get_rest['SnapshotSet'][delpos]['SnapshotId'])
                DeleteSnapshots_re = DeleteSnapshots(SecretId, SecretKey, SnapshotId, region)
                if DeleteSnapshots_re != False:
                        print('已经删除完成快照ID为{0}的快照，现在准备开始备份实例'.format(SnapshotId))
                        CreateInstanceSnapshot(SecretId, SecretKey, region, InstanceIds)
        else:
            print('当前快照数量存在问题，登录腾讯云后台检查删除多余的快照')
            time.sleep(5)
            exit()

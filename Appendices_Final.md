## ПРИЛОЖЕНИЯ

## Приложение А
### Фрагмент файла KursachNetwork.ned

```ned
import inet.common.scenario.ScenarioManager;
import inet.common.misc.ThruputMeteringChannel;
import inet.networklayer.configurator.ipv4.Ipv4NetworkConfigurator;
import inet.node.ethernet.EthernetSwitch;
import inet.node.inet.StandardHost;
import inet.node.ospfv2.OspfRouter;

network KursachNetwork
{
    parameters:
        int numBrHosts = default(2);
        int numAdminHosts = default(4);
        int numAccountingHosts = default(5);
        int numDirectorHosts = default(2);
        int numWarehouseHosts = default(7);
        int numKitchenHosts = default(7);
        int numHallHosts = default(5);
        @display("bgb=1700,1080");

        // Analytical coordinates for host groups
        int bAdmin = 4;
        int bAcc = 5;
        int bDir = 2;
        int bWar = 7;
        int bKit = 7;
        int bHall = 5;
        int bBr = 2;

        // Base coordinates (Top)
        double adminBaseX = 310 - (bAdmin-1)*30;
        double accBaseX = 310 - (bAcc-1)*30;
        double dirBaseX = 585 - (bDir-1)*52.5;
        double warBaseX = 960 - (bWar-1)*30;
        double kitBaseX = 1295 - (bKit-1)*30;
        double hallBaseX = 1345 - (bHall-1)*30;
        double br1Y = 120 - (bBr-1)*30;
        double br2Y = 260 - (bBr-1)*30;

        // Extra coordinates (Sides/Bottom)
        double adminExtraY = 480 - (numAdminHosts-bAdmin-1)*20;
        double accExtraY = 745 - (numAccountingHosts-bAcc-1)*20;
        double dirExtraY = 935 - (numDirectorHosts-bDir-1)*20;
        double kitExtraY = 500 - (numKitchenHosts-bKit-1)*20;
        double warExtraX = 960 - (numWarehouseHosts-bWar-1)*30;
        double hallExtraX = 1345 - (numHallHosts-bHall-1)*30;

    types:
        channel lanLink extends ThruputMeteringChannel
        {
            delay = uniform(0.1ms, 0.2ms);
            datarate = 100Mbps;
            thruputDisplayFormat = "u";
        }

        channel serverLanLink extends ThruputMeteringChannel
        {
            delay = uniform(0.05ms, 0.15ms);
            datarate = 1Gbps;
            thruputDisplayFormat = "u";
        }

        channel wanLink extends ThruputMeteringChannel
        {
            delay = uniform(4ms, 6ms);
            datarate = 20Mbps;
            thruputDisplayFormat = "u";
        }

        channel internetPrimary extends ThruputMeteringChannel
        {
            delay = uniform(9ms, 11ms);
            datarate = 30Mbps;
            thruputDisplayFormat = "u";
        }

        channel internetReserve extends ThruputMeteringChannel
        {
            delay = uniform(18ms, 22ms);
            datarate = 30Mbps;
            thruputDisplayFormat = "u";
        }

    submodules:
        configurator: Ipv4NetworkConfigurator {
            @display("p=120,40;is=s");
        }

        scenarioManager: ScenarioManager {
            @display("p=120,100;is=s");
        }

        externalResource: StandardHost {
            @display("i=device/server;p=260,120;fillcolor=lightgray");
        }

        inetSw: EthernetSwitch {
            @display("p=455,120");
        }

        isp: OspfRouter {
            @display("i=device/router;p=690,120;fillcolor=orange");
        }

        core: OspfRouter {
            @display("i=device/router;p=860,260;fillcolor=yellow");
        }

        hqSw: EthernetSwitch {
            @display("p=860,580");
        }

        hqSrv[2]: StandardHost {
            @display("i=device/server;p=760,455,row,200;fillcolor=lightgreen");
        }

        // --- ADMINISTRATION ---
        adminSw: EthernetSwitch {
            @display("p=310,480;i=device/switch");
        }
        adminPc[numAdminHosts > bAdmin ? bAdmin : numAdminHosts]: StandardHost {
            @display("i=device/pc;p=$adminBaseX,380,row,60;fillcolor=lightblue");
        }
        adminExtra[numAdminHosts > bAdmin ? numAdminHosts - bAdmin : 0]: StandardHost {
            @display("i=device/pc;p=210,$adminExtraY,column,40;fillcolor=lightblue");
        }

        // --- ACCOUNTING ---
        accSw: EthernetSwitch {
            @display("p=310,745;i=device/switch");
        }
        accPc[numAccountingHosts > bAcc ? bAcc : numAccountingHosts]: StandardHost {
            @display("i=device/pc;p=$accBaseX,645,row,60;fillcolor=lightyellow");
        }
        accExtra[numAccountingHosts > bAcc ? numAccountingHosts - bAcc : 0]: StandardHost {
            @display("i=device/pc;p=210,$accExtraY,column,40;fillcolor=lightyellow");
        }

        // --- DIRECTOR OFFICE ---
        dirSw: EthernetSwitch {
            @display("p=585,935;i=device/switch");
        }
        dirPc[numDirectorHosts > bDir ? bDir : numDirectorHosts]: StandardHost {
            @display("i=device/pc;p=$dirBaseX,835,row,105;fillcolor=lightgray");
        }
        dirExtra[numDirectorHosts > bDir ? numDirectorHosts - bDir : 0]: StandardHost {
            @display("i=device/pc;p=485,$dirExtraY,column,70;fillcolor=lightgray");
        }

        // --- WAREHOUSE ---
        warSw: EthernetSwitch {
            @display("p=960,935;i=device/switch");
        }
        warPc[numWarehouseHosts > bWar ? bWar : numWarehouseHosts]: StandardHost {
            @display("i=device/pc;p=$warBaseX,835,row,60;fillcolor=tan");
        }
        warExtra[numWarehouseHosts > bWar ? numWarehouseHosts - bWar : 0]: StandardHost {
            @display("i=device/pc;p=$warExtraX,1035,row,60;fillcolor=tan");
        }

        // --- KITCHEN ---
        kitSw: EthernetSwitch {
            @display("p=1295,500;i=device/switch");
        }
        kitPc[numKitchenHosts > bKit ? bKit : numKitchenHosts]: StandardHost {
            @display("i=device/pc;p=$kitBaseX,400,row,60;fillcolor=lightcyan");
        }
        kitExtra[numKitchenHosts > bKit ? numKitchenHosts - bKit : 0]: StandardHost {
            @display("i=device/pc;p=1395,$kitExtraY,column,40;fillcolor=lightcyan");
        }

        // --- SERVICE HALL ---
        hallSw: EthernetSwitch {
            @display("p=1345,860;i=device/switch");
        }
        hallPc[numHallHosts > bHall ? bHall : numHallHosts]: StandardHost {
            @display("i=device/pc;p=$hallBaseX,760,row,60;fillcolor=palegreen");
        }
        hallExtra[numHallHosts > bHall ? numHallHosts - bHall : 0]: StandardHost {
            @display("i=device/pc;p=$hallExtraX,960,row,60;fillcolor=palegreen");
        }

        // --- BRANCHES ---
        br1R: OspfRouter {
            @display("i=device/router;p=1175,120;fillcolor=yellow");
        }

        br1Sw: EthernetSwitch {
            @display("p=1295,120");
        }

        br1Host[numBrHosts]: StandardHost {
            @display("i=device/pc;p=1395,$br1Y,column,60;fillcolor=lightblue");
        }

        br2R: OspfRouter {
            @display("i=device/router;p=1175,260;fillcolor=yellow");
        }

        br2Sw: EthernetSwitch {
            @display("p=1295,260");
        }

        br2Host[numBrHosts]: StandardHost {
            @display("i=device/pc;p=1395,$br2Y,column,60;fillcolor=lightblue");
        }

    connections allowunconnected:
        // Admin connections
        for i=0..sizeof(adminPc)-1 {
            adminPc[i].ethg++ <--> lanLink <--> adminSw.ethg++;
        }
        for i=0..sizeof(adminExtra)-1 {
            adminExtra[i].ethg++ <--> lanLink <--> adminSw.ethg++;
        }
        adminSw.ethg++ <--> lanLink <--> hqSw.ethg++;

        // Accounting connections
        for i=0..sizeof(accPc)-1 {
            accPc[i].ethg++ <--> lanLink <--> accSw.ethg++;
        }
        for i=0..sizeof(accExtra)-1 {
            accExtra[i].ethg++ <--> lanLink <--> accSw.ethg++;
        }
        accSw.ethg++ <--> lanLink <--> hqSw.ethg++;

        // Director Office connections
        for i=0..sizeof(dirPc)-1 {
            dirPc[i].ethg++ <--> lanLink <--> dirSw.ethg++;
        }
        for i=0..sizeof(dirExtra)-1 {
            dirExtra[i].ethg++ <--> lanLink <--> dirSw.ethg++;
        }
        dirSw.ethg++ <--> lanLink <--> hqSw.ethg++;

        // Warehouse connections
        for i=0..sizeof(warPc)-1 {
            warPc[i].ethg++ <--> lanLink <--> warSw.ethg++;
        }
        for i=0..sizeof(warExtra)-1 {
            warExtra[i].ethg++ <--> lanLink <--> warSw.ethg++;
        }
        warSw.ethg++ <--> lanLink <--> hqSw.ethg++;

        // Kitchen connections
        for i=0..sizeof(kitPc)-1 {
            kitPc[i].ethg++ <--> lanLink <--> kitSw.ethg++;
        }
        for i=0..sizeof(kitExtra)-1 {
            kitExtra[i].ethg++ <--> lanLink <--> kitSw.ethg++;
        }
        kitSw.ethg++ <--> lanLink <--> hqSw.ethg++;

        // Service Hall connections
        for i=0..sizeof(hallPc)-1 {
            hallPc[i].ethg++ <--> lanLink <--> hallSw.ethg++;
        }
        for i=0..sizeof(hallExtra)-1 {
            hallExtra[i].ethg++ <--> lanLink <--> hallSw.ethg++;
        }
        hallSw.ethg++ <--> lanLink <--> hqSw.ethg++;

        for i=0..sizeof(hqSrv)-1 {
            hqSrv[i].ethg++ <--> serverLanLink <--> hqSw.ethg++;
        }

        core.ethg++ <--> serverLanLink <--> hqSw.ethg++;

        for i=0..sizeof(br1Host)-1 {
            br1Host[i].ethg++ <--> lanLink <--> br1Sw.ethg++;
        }

        for i=0..sizeof(br2Host)-1 {
            br2Host[i].ethg++ <--> lanLink <--> br2Sw.ethg++;
        }

        br1R.ethg++ <--> lanLink <--> br1Sw.ethg++;
        br1R.pppg++ <--> wanLink <--> core.pppg++;

        br2R.ethg++ <--> lanLink <--> br2Sw.ethg++;
        br2R.pppg++ <--> wanLink <--> core.pppg++;

        externalResource.ethg++ <--> lanLink <--> inetSw.ethg++;
        isp.ethg++ <--> lanLink <--> inetSw.ethg++;

        core.pppg++ <--> internetPrimary <--> isp.pppg++;
        core.pppg++ <--> internetReserve <--> isp.pppg++;
}
```

## Приложение Б
### Фрагмент файла omnetpp.ini

```ini
[General]
network = KursachNetwork
sim-time-limit = 60s
ned-path = .

result-dir = ../../03_results/omnetpp
output-vector-file = "${resultdir}/${configname}-${runnumber}.vec"
output-scalar-file = "${resultdir}/${configname}-${runnumber}.sca"

**.scalar-recording = true
**.vector-recording = true
**.statistic-recording = true

# Включаем запись PCAP
*.core.numPcapRecorders = 1
*.core.pcapRecorder[0].pcapFile = "/home/dev/6_sem/KURSACH_seti/03_results/pcap/${configname}-core.pcap"
*.core.pcapRecorder[0].packetFilter = "*"

*.core.ppp[2].numPcapRecorders = 1
*.core.ppp[2].pcapRecorder[0].pcapFile = "/home/dev/6_sem/KURSACH_seti/03_results/pcap/${configname}-ppp2.pcap"
*.core.ppp[3].numPcapRecorders = 1
*.core.ppp[3].pcapRecorder[0].pcapFile = "/home/dev/6_sem/KURSACH_seti/03_results/pcap/${configname}-ppp3.pcap"

*.hqSrv[*].numPcapRecorders = 1
*.hqSrv[0].pcapRecorder[0].pcapFile = "/home/dev/6_sem/KURSACH_seti/03_results/pcap/${configname}-hqSrv0.pcap"
*.hqSrv[1].pcapRecorder[0].pcapFile = "/home/dev/6_sem/KURSACH_seti/03_results/pcap/${configname}-hqSrv1.pcap"

*.externalResource.numApps = 1
*.externalResource.app[0].typename = "TcpGenericServerApp"
*.externalResource.app[0].localPort = 8080
*.externalResource.numPcapRecorders = 1
*.externalResource.pcapRecorder[0].pcapFile = "/home/dev/6_sem/KURSACH_seti/03_results/pcap/${configname}-external.pcap"

**.pcapRecorder[*].packetFilter = "*"

**.app[*].rtt.scalar-recording = true
**.app[*].rtt.vector-recording = true
**.app[*].rtt.result-recording-modes = "stats,vector"

cmdenv-express-mode = true
seed-set = ${runnumber}

# Настройки OSPF для быстрой сходимости
**.hasOspf = false
*.core.hasOspf = true
*.br1R.hasOspf = true
*.br2R.hasOspf = true
*.isp.hasOspf = true
**.ospf.helloInterval = 1s
**.ospf.routerDeadInterval = 4s
**.ospf.ospfConfig = xmldoc("ASConfig.xml")

**.configurator.config = xmldoc("routing.xml")
**.configurator.addStaticRoutes = true
**.configurator.addDefaultRoutes = true
**.configurator.addSubnetRoutes = true

**.crcMode = "computed"
**.fcsMode = "computed"
**.tcp.mss = 800
**.app[*].thinkTime = 0s
**.app[*].idleInterval = 0.2s
**.app[*].requestLength = 800B
**.app[*].replyLength = 5000B

*.hqSw.numEthInterfaces = 12
*.inetSw.numEthInterfaces = 4
*.br1Sw.numEthInterfaces = 8
*.br2Sw.numEthInterfaces = 8
*.adminSw.numEthInterfaces = 16
*.accSw.numEthInterfaces = 16
*.dirSw.numEthInterfaces = 16
*.warSw.numEthInterfaces = 16
*.kitSw.numEthInterfaces = 16
*.hallSw.numEthInterfaces = 16

*.hqSrv[0].numApps = 1
*.hqSrv[0].app[0].typename = "TcpGenericServerApp"
*.hqSrv[0].app[0].localPort = 1000

*.hqSrv[1].numApps = 1
*.hqSrv[1].app[0].typename = "TcpGenericServerApp"
*.hqSrv[1].app[0].localPort = 1001

# --- APPLICATION DEFINITIONS (Applied to all scenarios) ---
# Use wildcards to cover both Pc and Extra hosts

*.admin*[*].numApps = 3
*.admin*[*].app[0].typename = "TcpBasicClientApp"
*.admin*[*].app[0].connectAddress = "KursachNetwork.hqSrv[0]"
*.admin*[*].app[0].connectPort = 1000
*.admin*[*].app[0].startTime = uniform(2s, 5s)
*.admin*[*].app[0].idleInterval = exponential(1.0s)
*.admin*[*].app[0].requestLength = 800B
*.admin*[*].app[0].replyLength = 3200B
*.admin*[*].app[1].typename = "TcpBasicClientApp"
*.admin*[*].app[1].connectAddress = "KursachNetwork.externalResource"
*.admin*[*].app[1].connectPort = 8080
*.admin*[*].app[1].startTime = uniform(3s, 6s)
*.admin*[*].app[1].idleInterval = exponential(1.3s)
*.admin*[*].app[1].requestLength = 800B
*.admin*[*].app[1].replyLength = 4800B
*.admin*[*].app[2].typename = "PingApp"
*.admin*[*].app[2].destAddr = "KursachNetwork.hqSrv[0]"
*.admin*[*].app[2].startTime = uniform(4s, 7s)
*.admin*[*].app[2].sendInterval = uniform(0.9s,1.3s)
*.admin*[*].app[2].printPing = true

*.acc*[*].numApps = 2
*.acc*[*].app[0].typename = "TcpBasicClientApp"
*.acc*[*].app[0].connectAddress = "KursachNetwork.hqSrv[1]"
*.acc*[*].app[0].connectPort = 1001
*.acc*[*].app[0].startTime = uniform(2.5s, 5.5s)
*.acc*[*].app[0].idleInterval = exponential(0.8s)
*.acc*[*].app[0].requestLength = 800B
*.acc*[*].app[0].replyLength = 2400B
*.acc*[*].app[1].typename = "PingApp"
*.acc*[*].app[1].destAddr = "KursachNetwork.externalResource"
*.acc*[*].app[1].startTime = uniform(3.5s, 6.5s)
*.acc*[*].app[1].sendInterval = uniform(1.0s,1.4s)
*.acc*[*].app[1].printPing = true

*.dir*[*].numApps = 1
*.dir*[*].app[0].typename = "TcpBasicClientApp"
*.dir*[*].app[0].connectAddress = "KursachNetwork.hqSrv[0]"
*.dir*[*].app[0].connectPort = 1000
*.dir*[*].app[0].startTime = uniform(3s, 6s)
*.dir*[*].app[0].idleInterval = exponential(1.2s)
*.dir*[*].app[0].requestLength = 800B
*.dir*[*].app[0].replyLength = 4000B

*.war*[*].numApps = 1
*.war*[*].app[0].typename = "TcpBasicClientApp"
*.war*[*].app[0].connectAddress = "KursachNetwork.hqSrv[1]"
*.war*[*].app[0].connectPort = 1001
*.war*[*].app[0].startTime = uniform(2.5s, 5.5s)
*.war*[*].app[0].idleInterval = exponential(0.7s)
*.war*[*].app[0].requestLength = 800B
*.war*[*].app[0].replyLength = 2800B

*.kit*[*].numApps = 1
*.kit*[*].app[0].typename = "TcpBasicClientApp"
*.kit*[*].app[0].connectAddress = "KursachNetwork.hqSrv[0]"
*.kit*[*].app[0].connectPort = 1000
*.kit*[*].app[0].startTime = uniform(3.5s, 6.5s)
*.kit*[*].app[0].idleInterval = exponential(0.9s)
*.kit*[*].app[0].requestLength = 800B
*.kit*[*].app[0].replyLength = 2000B

*.hall*[*].numApps = 1
*.hall*[*].app[0].typename = "TcpBasicClientApp"
*.hall*[*].app[0].connectAddress = "KursachNetwork.externalResource"
*.hall*[*].app[0].connectPort = 8080
*.hall*[*].app[0].startTime = uniform(3s, 6s)
*.hall*[*].app[0].idleInterval = exponential(1.1s)
*.hall*[*].app[0].requestLength = 800B
*.hall*[*].app[0].replyLength = 5200B

*.br1Host[*].numApps = 2
*.br1Host[*].app[0].typename = "TcpBasicClientApp"
*.br1Host[*].app[0].connectAddress = "KursachNetwork.hqSrv[1]"
*.br1Host[*].app[0].connectPort = 1001
*.br1Host[*].app[0].startTime = uniform(4s, 7s)
*.br1Host[*].app[0].idleInterval = exponential(1.6s)
*.br1Host[*].app[0].requestLength = 800B
*.br1Host[*].app[0].replyLength = 2600B
*.br1Host[*].app[1].typename = "PingApp"
*.br1Host[*].app[1].destAddr = "KursachNetwork.hqSrv[1]"
*.br1Host[*].app[1].startTime = uniform(5s, 8s)
*.br1Host[*].app[1].sendInterval = uniform(1.1s,1.6s)
*.br1Host[*].app[1].printPing = true

*.br2Host[*].numApps = 1
*.br2Host[*].app[0].typename = "TcpBasicClientApp"
*.br2Host[*].app[0].connectAddress = "KursachNetwork.externalResource"
*.br2Host[*].app[0].connectPort = 8080
*.br2Host[*].app[0].startTime = uniform(4.5s, 7.5s)
*.br2Host[*].app[0].idleInterval = exponential(1.8s)
*.br2Host[*].app[0].requestLength = 800B
*.br2Host[*].app[0].replyLength = 5000B

**.numApps = 0
**.app[*].typename = ""

[Config A_Base]
description = "A: base topology, reserve channel disabled"
seed-set = 100
*.scenarioManager.script = xml( \
    "<script>" + \
    "<at t='1s'><shutdown module='core.ppp[3]'/></at>" + \
    "</script>")

[Config B_ReserveEnabled]
description = "B: reserve Internet channel enabled"
seed-set = 200

# Оптимизации TCP для стабильности при наличии OSPF и двух каналов
**.tcp.rtxTimeoutMin = 0.1s
**.tcp.rtxTimeoutMax = 0.5s
**.tcp.delayedAcksEnabled = false
**.tcp.nagleEnabled = false

*.scenarioManager.script = xml("<empty/>")

[Config C_FailurePrimary]
description = "C: primary Internet channel fails and is restored"
seed-set = 300
cmdenv-express-mode = true

# Ускоряем TCP для быстрого обнаружения обрыва
**.tcp.rtxTimeoutMin = 0.2s
**.tcp.rtxTimeoutMax = 1s
**.tcp.delayedAcksEnabled = false

# Делаем трафик более плотным
*.admin*[*].app[1].idleInterval = exponential(0.2s)
*.hall*[*].app[0].idleInterval = exponential(0.2s)
*.br2Host[*].app[0].idleInterval = exponential(0.2s)

*.admin*[*].app[1].reconnectInterval = 1s
*.hall*[*].app[0].reconnectInterval = 1s
*.br2Host[*].app[0].reconnectInterval = 1s

*.scenarioManager.script = xml( \
    "<script>" + \
    "<at t='15s'><shutdown module='core.ppp[2]'/></at>" + \
    "<at t='15s'><shutdown module='isp.ppp[0]'/></at>" + \
    "<at t='35s'><startup module='core.ppp[2]'/></at>" + \
    "<at t='35s'><startup module='isp.ppp[0]'/></at>" + \
    "</script>")

[Config D_ScaleUp]
description = "D: increased number of hosts from 30 to 43 as per requirements (N+5=13 extra)"
seed-set = 400
*.numAdminHosts = 5
*.numAccountingHosts = 7
*.numDirectorHosts = 3
*.numWarehouseHosts = 10
*.numKitchenHosts = 9
*.numHallHosts = 9
*.numBrHosts = 2

*.scenarioManager.script = xml("<empty/>")
```

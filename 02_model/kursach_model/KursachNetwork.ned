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

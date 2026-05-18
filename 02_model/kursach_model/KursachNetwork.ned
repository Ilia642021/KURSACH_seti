import inet.common.scenario.ScenarioManager;
import inet.common.misc.ThruputMeteringChannel;
import inet.networklayer.configurator.ipv4.Ipv4NetworkConfigurator;
import inet.node.ethernet.EthernetSwitch;
import inet.node.inet.StandardHost;
import inet.node.ospfv2.OspfRouter;

network KursachNetwork
{
    parameters:
        int numHqHosts = default(30);
        int numBrHosts = default(2);
        @display("bgb=1400,1000");   // enlarged canvas height

    types:
        module Cabinet
        {
            gates:
                inout ethg[5];
            submodules:
                h1: StandardHost { @display("p=50,50;i=device/pc;fillcolor=lightblue"); }
                h2: StandardHost { @display("p=150,50;i=device/pc;fillcolor=lightblue"); }
                h3: StandardHost { @display("p=100,100;i=device/pc;fillcolor=lightblue"); }
                h4: StandardHost { @display("p=50,150;i=device/pc;fillcolor=lightblue"); }
                h5: StandardHost { @display("p=150,150;i=device/pc;fillcolor=lightblue"); }
            connections:
                h1.ethg++ <--> { @display("m=white"); } <--> ethg++;
                h2.ethg++ <--> { @display("m=white"); } <--> ethg++;
                h3.ethg++ <--> { @display("m=white"); } <--> ethg++;
                h4.ethg++ <--> { @display("m=white"); } <--> ethg++;
                h5.ethg++ <--> { @display("m=white"); } <--> ethg++;
        }

        channel lanLink extends ThruputMeteringChannel
        {
            delay = 0.1ms;
            datarate = 100Mbps;
            thruputDisplayFormat = "u";
        }

        channel wanLink extends ThruputMeteringChannel
        {
            delay = 5ms;
            datarate = 20Mbps;
            thruputDisplayFormat = "u";
        }

        channel internetPrimary extends ThruputMeteringChannel
        {
            delay = 20ms;
            datarate = 30Mbps;
            thruputDisplayFormat = "u";
        }

        channel internetReserve extends ThruputMeteringChannel
        {
            delay = 10ms;
            datarate = 30Mbps;
            thruputDisplayFormat = "u";
        }

    submodules:

        configurator: Ipv4NetworkConfigurator {
            @display("p=150,50;is=s");
        }

        scenarioManager: ScenarioManager {
            @display("p=150,120;is=s");
        }

        //
        // Internet segment
        //
        inetHost: StandardHost {
            @display("i=device/cloud;p=270,100;fillcolor=lightgray");
        }

        inetSw: EthernetSwitch {
            @display("p=470,100");
        }

        isp: OspfRouter {
            @display("i=device/router;p=750,100;fillcolor=orange");
        }

        //
        // Core
        //
        core: OspfRouter {
            @display("i=device/router;p=750,250;fillcolor=yellow");
        }

        //
        // HQ
        //
        hqSw: EthernetSwitch {
            @display("p=750,550");   // centered between cabinets
        }

        // Vertical server column (unchanged)
        hqSrv[2]: StandardHost {
            @display("i=device/server;p=650,420,row,200;fillcolor=lightgreen");
        }

        // ---------- Six cabinets (visual groups) ----------
        cab1: Cabinet { @display("p=350,400;bgb=200,200"); }
        cab2: Cabinet { @display("p=350,600;bgb=200,200"); }
        cab3: Cabinet { @display("p=550,800;bgb=200,200"); }
        cab4: Cabinet { @display("p=900,800;bgb=200,200"); }
        cab5: Cabinet { @display("p=1100,400;bgb=200,200"); }
        cab6: Cabinet { @display("p=1100,600;bgb=200,200"); }

        // Extra hosts for scaling (Scenario D)
        extraHost[numHqHosts > 30 ? numHqHosts - 30 : 0]: StandardHost {
            @display("i=device/pc;p=350,850,row,60;fillcolor=cyan");
        }

        //
        // Branch 1
        //
        br1R: OspfRouter {
            @display("i=device/router;p=1100,100;fillcolor=yellow");
        }

        br1Sw: EthernetSwitch {
            @display("p=1200,100");
        }

        br1Host[numBrHosts]: StandardHost {
            @display("i=device/pc;p=1320,80,col,60;fillcolor=lightblue");
        }

        //
        // Branch 2
        //
        br2R: OspfRouter {
            @display("i=device/router;p=1100,250;fillcolor=yellow");
        }

        br2Sw: EthernetSwitch {
            @display("p=1200,250");
        }

        br2Host[numBrHosts]: StandardHost {
            @display("i=device/pc;p=1320,230,col,60;fillcolor=lightblue");
        }

    connections allowunconnected:

        // Connect all hosts from the six cabinets to hqSw
        for i=0..4 {
            cab1.ethg[i] <--> lanLink <--> hqSw.ethg++;
            cab2.ethg[i] <--> lanLink <--> hqSw.ethg++;
            cab3.ethg[i] <--> lanLink <--> hqSw.ethg++;
            cab4.ethg[i] <--> lanLink <--> hqSw.ethg++;
            cab5.ethg[i] <--> lanLink <--> hqSw.ethg++;
            cab6.ethg[i] <--> lanLink <--> hqSw.ethg++;
        }

        // Connect extra hosts for scaling
        for i=0..(numHqHosts > 30 ? numHqHosts - 31 : -1) {
            extraHost[i].ethg++ <--> lanLink <--> hqSw.ethg++;
        }

        // Servers (unchanged)
        for i=0..1 {
            hqSrv[i].ethg++ <--> lanLink <--> hqSw.ethg++;
        }

        // Core uplink
        core.ethg++ <--> lanLink <--> hqSw.ethg++;

        //
        // Branch 1 (unchanged)
        //
        for i=0..1 {
            br1Host[i].ethg++ <--> lanLink <--> br1Sw.ethg++;
        }
        br1R.ethg++ <--> lanLink <--> br1Sw.ethg++;
        br1R.pppg++ <--> wanLink <--> core.pppg++;

        //
        // Branch 2 (unchanged)
        //
        for i=0..1 {
            br2Host[i].ethg++ <--> lanLink <--> br2Sw.ethg++;
        }
        br2R.ethg++ <--> lanLink <--> br2Sw.ethg++;
        br2R.pppg++ <--> wanLink <--> core.pppg++;

        //
        // Internet edge (unchanged)
        //
        inetHost.ethg++ <--> lanLink <--> inetSw.ethg++;
        isp.ethg++ <--> lanLink <--> inetSw.ethg++;

        //
        // ISP uplinks (unchanged)
        //
        core.pppg++ <--> internetPrimary <--> isp.pppg++;
        core.pppg++ <--> internetReserve <--> isp.pppg++;
}
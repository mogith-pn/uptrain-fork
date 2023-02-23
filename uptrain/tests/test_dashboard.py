import uptrain
import random
import numpy as np


if __name__ == "__main__":
# def test_dashboard():
    cfg = {
        "st_logging": True,
        "logging_args": {
            # For slack alerts, add your webhook URL
            # Checkout https://api.slack.com/messaging/webhooks
            'slack_webhook_url': None,
            'dashboard_port': 50010,
        }
    }
    fw = uptrain.Framework(cfg)

    dashboard_name = "count_dashboard"
    for count in [0, 50, 100]:
        data = [count + random.randint(1, 100) for _ in range(100)]
        fw.log_handler.add_histogram(
            "multiple_histograms",
            data,
            dashboard_name,
            file_name="random(1,100) + " + str(count)
        )

    data = np.random.normal(size=1000)
    fw.log_handler.add_histogram(
        "single_histograms",
        data,
        dashboard_name,
    )

    fw.log_handler.add_alert(
        "Alerting",
        "A test alert",
        dashboard_name
    )

    line1 = [i + random.randint(1, 10) for i in range(100)]
    line2 = [i + random.randint(10, 20) for i in range(100)]

    for i,_ in enumerate(line1):
        fw.log_handler.add_scalars(
            "2 plots",
            {"y_value": line1[i]},
            i,
            dashboard_name,
            file_name='y_1',
        )
        fw.log_handler.add_scalars(
            "2 lines",
            {"y_value": line2[i]},
            i,
            dashboard_name,
            file_name='y_2',
        )
        fw.log_handler.add_scalars(
            "1 line",
            {"y_value": line2[i]+10},
            i,
            dashboard_name,
        )
        

    bar1_y = [i for i in range(5)]
    bar1_x = ["date: " + str(i) for i in range(5)]
    bar1_dict = dict(zip(bar1_x, bar1_y))

    bar2_y = [i for i in range(5,-1,-1)]
    bar2_x = ["date: " + str(i) for i in range(5)]
    bar2_dict = dict(zip(bar2_x, bar2_y))

    bar_dict = {'bar1': bar1_dict, 'bar2': bar2_dict}

    fw.log_handler.add_bar_graphs(
        "random bars",
        bar_dict,
        dashboard_name,
    )

    clusters = np.random.choice([0, 1], size=(100), p=[0.1, 0.9])
    umap = []
    for label in clusters:
        if label==0:
            umap.append(np.random.normal([0,0,0], 0.5, 3))
        else:
            umap.append(np.random.normal([1,1,1], 0.5, 3))

    umap_data = {"umap": umap, "clusters": clusters}

    fw.log_handler.add_histogram(
        "umap_and_clusters",
        umap_data,
        dashboard_name
    )

    
import json
from urllib.parse import quote

import pandas as pd
from matplotlib import dates as mpl_dates
from matplotlib import pyplot as plt, ticker
from requests import get


class ChartCreator:
    def __init__(self):
        self.data = None
        self.chart_specs = None
        self.title = None

    def __set_all_interval(self):
        n = len(self.data['data']['all']['values'])
        return 1 if n < 7 else n

    def __update_chart_specs(self):
        # time chart specs dict contains tuples (time_interval, date_format, unit)
        self.chart_specs = {
            "week": (1, "%b %d", "s"),
            "month": (4, "%b %d %Y", "s"),
            "year": (52, "%b %d %Y", None),
            "all": (self.__set_all_interval() // 7, "%b %d %Y", None),
        }

    def __get_data(self, name: str):
        url = f"https://steamfolio.com/api/Graph/itemChart?name={quote(name)}"
        response = get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            "Cookie": "currency=PLN"})
        self.data = json.loads(response.content)
        self.__update_chart_specs()

    def get_charts(self, name: str, chart_types: list):
        self.__get_data(name)
        self.title = name

        for chart_type in chart_types:
            self.__save_plot(chart_type)

    def __save_plot(self, chart_type: str):
        df = pd.DataFrame(self.data['data'][chart_type]['values'])
        df['time'] = pd.to_datetime(df['time'], unit=self.chart_specs[chart_type][2])
        df = df.sort_values('time', ascending=True)

        plt.style.use("style.mplstyle")

        time_data = df['time']
        value_data = df['value']

        fig, ax = plt.subplots(figsize=(9, 3), constrained_layout=True)

        plt.grid()

        ax.plot(time_data, value_data)
        ax.set_title(f"{self.title} [{chart_type}]")

        date_format = mpl_dates.DateFormatter(self.chart_specs[chart_type][1])
        ax.xaxis.set_major_formatter(date_format)
        ax.xaxis.set_major_locator(mpl_dates.DayLocator(interval=self.chart_specs[chart_type][0]))
        ax.set_xlim(min(time_data), max(time_data))

        yticks = ax.get_yticks()

        ax.set_yticks(yticks)
        diff = yticks[1] - yticks[0]

        def y_format(y, pos):
            return f"{y:.2f} zł"

        ax.yaxis.set_major_formatter(ticker.FuncFormatter(y_format))
        ax.set_ylim([min(value_data) - diff, max(value_data) + diff])

        ax2 = ax.twinx()
        ax2.set_yticks(yticks)
        ax2.yaxis.set_major_formatter(ticker.FuncFormatter(y_format))
        ax2.set_ylim([min(value_data) - diff, max(value_data) + diff])

        plt.savefig(f'images/{chart_type}.png')

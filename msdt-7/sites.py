import asyncio
import csv
import time
from dataclasses import dataclass
from typing import Optional

from aiohttp import ClientSession, ClientError


@dataclass
class SiteResult:
    url: str
    status: Optional[int]
    response_time: Optional[float]
    error: Optional[str]


async def check_site(session: ClientSession, url: str) -> SiteResult:
    start_time = time.perf_counter()

    try:
        async with session.get(url, timeout=10) as response:
            await response.text()
            response_time = round(time.perf_counter() - start_time, 3)

            return SiteResult(
                url=url,
                status=response.status,
                response_time=response_time,
                error=None,
            )

    except asyncio.TimeoutError:
        return SiteResult(
            url=url,
            status=None,
            response_time=None,
            error="Превышено время ожидания",
        )

    except ClientError as error:
        return SiteResult(
            url=url,
            status=None,
            response_time=None,
            error=str(error),
        )


async def check_sites(urls: list[str]) -> list[SiteResult]:
    async with ClientSession() as session:
        tasks = []

        for url in urls:
            task = asyncio.create_task(check_site(session, url))
            tasks.append(task)

        results = await asyncio.gather(*tasks)

    return results


def print_results(results: list[SiteResult]) -> None:
    print("Результаты проверки сайтов:\n")

    for result in results:
        if result.error is None:
            print(
                f"{result.url} | статус: {result.status} | "
                f"время ответа: {result.response_time} сек."
            )
        else:
            print(f"{result.url} | ошибка: {result.error}")


def save_results(results: list[SiteResult], filename: str) -> None:
    with open(filename, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter=";")

        writer.writerow(["url", "status", "response_time", "error"])

        for result in results:
            writer.writerow([
                result.url,
                result.status,
                result.response_time,
                result.error,
            ])


def analyze_results(results: list[SiteResult]) -> None:
    successful = [result for result in results if result.error is None]
    failed = [result for result in results if result.error is not None]

    print("\nСтатистика:")
    print(f"Всего сайтов: {len(results)}")
    print(f"Успешно проверено: {len(successful)}")
    print(f"С ошибками: {len(failed)}")

    if successful:
        average_time = sum(
            result.response_time for result in successful
        ) / len(successful)

        print(f"Среднее время ответа: {round(average_time, 3)} сек.")


async def main() -> None:
    urls = [
        "https://www.google.com",
        "https://www.github.com",
        "https://www.python.org",
        "https://aur.archlinux.org",
        "https://wiki.archlinux.org",
        "https://distrowatch.com",
    ]

    results = await check_sites(urls)

    print_results(results)
    analyze_results(results)
    save_results(results, "site_check_results.csv")


if __name__ == "__main__":
    asyncio.run(main())
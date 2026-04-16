# src/services/scraper.py
import logging
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from .models import Project
from ..config import SIP_BASE_URL

logger = logging.getLogger(__name__)


class ScraperService:
    """Scraper para o portal SIP da UFLA."""
    
    def __init__(self, base_url: str = SIP_BASE_URL, timeout: int = 10):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Linux; U) Gecko/20100101 Firefox/100.0"
        })
    
    def get_courses(self) -> dict[str, str]:
        """Extrai links de cursos disponíveis."""
        try:
            response = self.session.get(self.base_url, timeout=self.timeout)
            response.raise_for_status()
            response.encoding = "utf-8"
        except requests.RequestException as e:
            logger.error(f"Erro ao buscar cursos: {e}")
            raise
        
        soup = BeautifulSoup(response.text, "html.parser")
        courses = {}
        
        for link in soup.find_all("a", class_="botoes_de_menu"):
            course_name = link.get_text(strip=True)
            course_url = urljoin(self.base_url, link.get("href", ""))
            courses[course_name] = course_url
        
        logger.info(f"Encontrados {len(courses)} cursos")
        return courses
    
    def get_project_links(self, course_urls: dict[str, str]) -> list[str]:
        """Extrai URLs de projetos de cada curso."""
        links = []
        total = len(course_urls)
        
        for idx, (course_name, url) in enumerate(course_urls.items(), 1):
            logger.info(f"Buscando projetos do curso '{course_name}' ({idx}/{total})")
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                response.encoding = "utf-8"
            except requests.RequestException as e:
                logger.warning(f"Falha ao acessar {course_name}: {e}")
                continue
            
            soup = BeautifulSoup(response.text, "html.parser")
            for link in soup.find_all("a", href=True):
                href = link.get("href", "")
                if "index.php?dados=" in href:
                    full_url = urljoin(url, href)
                    links.append(full_url)
        
        logger.info(f"Total de URLs de projetos encontradas: {len(links)}")
        return links
    
    def scrape_projects(self, project_urls: list[str]) -> list[Project]:
        """Extrai informações detalhadas de cada projeto."""
        projects = []
        total = len(project_urls)
        
        for idx, url in enumerate(project_urls, 1):
            logger.info(f"Processando projeto {idx}/{total}")
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                response.encoding = "utf-8"
            except requests.RequestException as e:
                logger.warning(f"Falha ao scrape {url}: {e}")
                continue
            
            soup = BeautifulSoup(response.text, "html.parser")
            paragraphs = soup.find_all("p", class_="paragrafo_padrao_com_borda_inferior")
            project_data = {}
            for p in paragraphs:
                span = p.find("span")
                if not span:
                    continue
                key = span.get_text(strip=True)
                value = p.get_text(strip=True).replace(key, "", 1).strip()
                project_data[key] = value
            
            if "Título:" in project_data and "Resumo:" in project_data:
                project = Project.from_dict(project_data)
                projects.append(project)
        
        logger.info(f"Total de projetos extraídos: {len(projects)}")
        return projects
    
    def close(self):
        """Fecha a sessão HTTP."""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
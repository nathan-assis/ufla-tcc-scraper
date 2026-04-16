# scripts/scrape.py
"""Script para scraping de projetos."""
import logging
from pathlib import Path

from src.config import OUTPUT_DIR
from src.services.scraper import ScraperService

logger = logging.getLogger(__name__)


def main(courses: list[str]):
    """Scrape projetos dos cursos especificados."""
    logger.info(f"Iniciando scraping para cursos: {courses}")
    
    with ScraperService() as scraper:
        all_courses = scraper.get_courses()
        
        # Filtrar apenas os cursos solicitados
        selected_courses = {name: url for name, url in all_courses.items() if name in courses}
        
        if not selected_courses:
            logger.error(f"Nenhum dos cursos {courses} encontrado. Cursos disponíveis: {list(all_courses.keys())}")
            return
        
        logger.info(f"Cursos selecionados: {list(selected_courses.keys())}")
        
        project_urls = scraper.get_project_links(selected_courses)
        projects = scraper.scrape_projects(project_urls)
        
        # Salvar CSV
        csv_path = OUTPUT_DIR / "dados_sip.csv"
        from src.data.csv_handler import CSVHandler
        CSVHandler.save(projects, csv_path)
        
        logger.info(f"Scraping concluído. {len(projects)} projetos salvos em {csv_path}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python scripts/scrape.py 'Curso1' 'Curso2'")
        sys.exit(1)
    
    courses = sys.argv[1:]
    main(courses)
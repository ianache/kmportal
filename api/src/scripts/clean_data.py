"""
Script para limpiar todos los datos de documentos, dominios y ontología.

Uso:
    cd api
    python -m scripts.clean_data

Este script elimina:
- PostgreSQL: Todos los documentos, dominios, accesos, diagramas y jobs
- Neo4j: Todos los nodos OWL_Class y OWL_Property
- ChromaDB: Todas las colecciones de vectores (opcional)

⚠️ ADVERTENCIA: Esta operación no se puede deshacer.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import AsyncSessionLocal, engine
from db.neo4j_client import get_neo4j, close_neo4j
from core.logging_config import configure_logging, get_logger

# Configure logging
configure_logging(log_level="INFO")
logger = get_logger(__name__)


async def clean_postgresql():
    """Eliminar todos los documentos, dominios y datos relacionados de PostgreSQL."""
    logger.info("=== PostgreSQL: Iniciando limpieza ===")
    
    async with AsyncSessionLocal() as session:
        try:
            # Eliminar en orden correcto respetando foreign keys
            
            # 1. Ingestion jobs (depende de documents)
            result = await session.execute(text("DELETE FROM ingestion_jobs"))
            logger.info(f"✓ Eliminados {result.rowcount} registros de ingestion_jobs")
            
            # 2. Documents
            result = await session.execute(text("DELETE FROM documents"))
            doc_count = result.rowcount
            logger.info(f"✓ Eliminados {doc_count} documentos")
            
            # 3. Ontology diagrams (depende de domains)
            result = await session.execute(text("DELETE FROM ontology_diagrams"))
            logger.info(f"✓ Eliminados {result.rowcount} diagramas de ontología")
            
            # 4. Domain access (depende de domains)
            result = await session.execute(text("DELETE FROM domain_access"))
            logger.info(f"✓ Eliminados {result.rowcount} registros de acceso a dominios")
            
            # 5. Domains (después de eliminar dependencias)
            result = await session.execute(text("DELETE FROM domains"))
            domain_count = result.rowcount
            logger.info(f"✓ Eliminados {domain_count} dominios")
            
            await session.commit()
            
            logger.info(f"✅ PostgreSQL limpieza completa: {doc_count} documentos, {domain_count} dominios eliminados")
            return doc_count, domain_count
            
        except Exception as e:
            await session.rollback()
            logger.error(f"❌ Error limpiando PostgreSQL: {e}")
            raise


async def clean_neo4j():
    """Eliminar todos los nodos OWL_Class y OWL_Property de Neo4j."""
    logger.info("=== Neo4j: Iniciando limpieza ===")
    
    driver = await get_neo4j()
    
    try:
        async with driver.session() as session:
            # Contar antes de eliminar
            count_result = await session.run(
                "MATCH (n) WHERE n:OWL_Class OR n:OWL_Property RETURN count(n) as total"
            )
            record = await count_result.single()
            total_before = record["total"] if record else 0
            
            # Eliminar nodos OWL
            result = await session.run(
                "MATCH (n) WHERE n:OWL_Class OR n:OWL_Property DETACH DELETE n"
            )
            summary = await result.consume()
            
            logger.info(f"✓ Eliminados {summary.counters.nodes_deleted} nodos OWL de Neo4j")
            
            # Verificar que no queden nodos OWL
            verify_result = await session.run(
                "MATCH (n) WHERE n:OWL_Class OR n:OWL_Property RETURN count(n) as total"
            )
            record = await verify_result.single()
            remaining = record["total"] if record else 0
            
            if remaining == 0:
                logger.info(f"✅ Neo4j limpieza completa: {total_before} nodos OWL eliminados")
            else:
                logger.warning(f"⚠️ Quedan {remaining} nodos OWL en Neo4j")
            
            return total_before
            
    except Exception as e:
        logger.error(f"❌ Error limpiando Neo4j: {e}")
        raise


async def clean_chromadb():
    """Eliminar todas las colecciones de ChromaDB (opcional)."""
    logger.info("=== ChromaDB: Iniciando limpieza ===")
    
    try:
        import chromadb
        from core.config import settings
        
        # Conectar a ChromaDB
        chroma_host = getattr(settings, 'chroma_host', 'localhost')
        chroma_port = getattr(settings, 'chroma_port', 8000)
        
        client = chromadb.HttpClient(host=chroma_host, port=chroma_port)
        
        # Listar colecciones
        collections = client.list_collections()
        logger.info(f"Encontradas {len(collections)} colecciones en ChromaDB")
        
        # Eliminar cada colección
        deleted = 0
        for collection in collections:
            try:
                client.delete_collection(collection.name)
                logger.info(f"✓ Eliminada colección: {collection.name}")
                deleted += 1
            except Exception as e:
                logger.warning(f"⚠️ No se pudo eliminar colección {collection.name}: {e}")
        
        logger.info(f"✅ ChromaDB limpieza completa: {deleted}/{len(collections)} colecciones eliminadas")
        return deleted
        
    except ImportError:
        logger.info("ℹ️ ChromaDB no disponible, saltando...")
        return 0
    except Exception as e:
        logger.error(f"❌ Error limpiando ChromaDB: {e}")
        return 0


async def main():
    """Función principal de limpieza."""
    logger.info("=" * 60)
    logger.info("🧹 INICIANDO LIMPIEZA COMPLETA DE DATOS")
    logger.info("=" * 60)
    logger.info("")
    logger.info("⚠️  ESTA OPERACIÓN ELIMINARÁ:")
    logger.info("   - Todos los documentos de PostgreSQL")
    logger.info("   - Todos los dominios de PostgreSQL")
    logger.info("   - Todos los accesos a dominios")
    logger.info("   - Todos los diagramas de ontología")
    logger.info("   - Todos los nodos OWL_Class de Neo4j")
    logger.info("   - Todos los nodos OWL_Property de Neo4j")
    logger.info("   - Todas las colecciones de ChromaDB")
    logger.info("")
    
    # Confirmación interactiva (opcional en desarrollo)
    import os
    if os.getenv("SKIP_CONFIRM") != "true":
        response = input("¿Estás seguro? Escribe 'SI' para continuar: ")
        if response.strip().upper() != "SI":
            logger.info("❌ Operación cancelada por el usuario")
            return
    
    logger.info("")
    logger.info("Iniciando limpieza...")
    logger.info("")
    
    results = {
        "postgresql": {"documents": 0, "domains": 0},
        "neo4j": {"nodes": 0},
        "chromadb": {"collections": 0}
    }
    
    try:
        # Limpiar PostgreSQL
        doc_count, domain_count = await clean_postgresql()
        results["postgresql"]["documents"] = doc_count
        results["postgresql"]["domains"] = domain_count
        
        # Limpiar Neo4j
        owl_count = await clean_neo4j()
        results["neo4j"]["nodes"] = owl_count
        
        # Limpiar ChromaDB
        chroma_count = await clean_chromadb()
        results["chromadb"]["collections"] = chroma_count
        
        # Resumen
        logger.info("")
        logger.info("=" * 60)
        logger.info("✅ LIMPIEZA COMPLETADA EXITOSAMENTE")
        logger.info("=" * 60)
        logger.info(f"📊 PostgreSQL: {doc_count} documentos, {domain_count} dominios")
        logger.info(f"📊 Neo4j: {owl_count} nodos OWL")
        logger.info(f"📊 ChromaDB: {chroma_count} colecciones")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error("")
        logger.error("=" * 60)
        logger.error("❌ ERROR DURANTE LA LIMPIEZA")
        logger.error("=" * 60)
        logger.error(f"Error: {e}")
        sys.exit(1)
    finally:
        # Cerrar conexiones
        await close_neo4j()
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

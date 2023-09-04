#######################################
# Classe para recortar um raster 
# para cada feição do shapefile. 
# A classe também cria a pasta e salva 
# o arquivo com o nome da camada da 
# feição do shapefile.
#
# Author: <Rogerio Vidal de Siqueira>
# Email: <rogeriovidalsiqueira@gmail.com>
# Date: 04/09/2023
# Version: 1.0
#######################################

import os
import re
import glob
import shapely
import rasterio
import unidecode
import geopandas as gpd
from rasterio.mask import mask

class RecortarRaster:
    """ 
        O intuito de desenvolver essa classe foi facilitar 
        o processo de recortar um raster para cada feição do shapefile. 
        
        Essa classe também cria a pasta e salva o arquivo com o nome da camada da feição do shapefile.
    
    """
    def carregar_vetor(self, path_shp):

        if os.path.isfile(path_shp) == True:
            #read shapefile
            gdf = gpd.read_file(path_shp)
            return gdf
        else:
            print("ARQUIVO NÃO ENCONTRADO!!!")

    def pegar_numero(self, string):
        """ Pega o primeiro número da string, no caso o ano que está registrado no nome do arquivo raster.
        Ex: Reclass_Mapbiomas1985-APM.tif -> 1985 """
        import re
        return re.findall(r'\d+',string)[0]

    def criar_pasta(self, nome):
        # Função que cria diretórios

        try:
            return os.mkdir(nome)
        except OSError as error:
            print(error)

    def clear_caracter_especial(self, str_velha):
        
        #Remover caracteres especiais
        #Exemplo: APM - SÃO BARTOLOMEU (Parte Norte) -> apm_sao_bartolomeu_parte_norte_

        str_nova = str_velha.lower()

        str_nova = unidecode.unidecode(str_nova)      

        str_nova = re.sub(
                        r"[^a-zA-Z0-9]",
                        "_",
                        str_nova
            ).replace("___","_").replace("__","_")
                
        return str_nova

    def recortar_raster(self, gdf, path_tif):
        #Retorar o raster a partir de cada feição do shp

        #Loop para interar em cada feição do shp
        for i in range(len(gdf)):
            #Salver as coordenadas em uma lista
            shape = []
            #Pegar coordenadas conforme a necessidade de entreda para recortar
            coord = shapely.geometry.mapping(gdf)["features"][i]["geometry"]
            shape.append(coord)
            #Nome da feição do shp
            nome_pasta = gdf.loc[i]['nome']
            #Nome limpo
            nome_arquivo = self.clear_caracter_especial(nome_pasta)
            #Criar pasta
            self.criar_pasta(nome_pasta)
            #Pegar o ano
            ano = self.pegar_numero(path_tif)

            if os.path.isfile(path_tif) == True:
                #Carregar um raster
                with rasterio.open(path_tif) as src:
                    
                    """
                    Aplica-se recursos no shp como um máscara no raster e
                    define todos os pixels fora dos recursos como zero. 

                    Como 'crop=True' neste exemplo, a extensão do raster também
                    é definida como a extensão dos recursos no shapefile. Podemos
                    então usar a transformação espacial atualizada e a altura e 
                    largura do raster para gravar o raster mascarado em um novo
                    arquivo.

                    """
                    out_image, out_transform = mask(src, shape, crop=True)
                    out_meta = src.meta
                    out_meta.update({'driver':'GTiff',
                        'height':out_image.shape[1],
                        'width':out_image.shape[2],
                        'transform':out_transform})
                    #caminho e nome do arquivo de saída 
                    out_tif = os.path.join(nome_pasta,f"{nome_arquivo}_{ano}.tif")
                    #Visualizar a saída
                    print(out_tif)
                
                #Salvar o arquivo recortado
                with rasterio.open(out_tif, "w", **out_meta) as dest:
                    dest.write(out_image)
                    
            else:
                print("ARQUIVO NÃO ENCONTRADO!!!")

if __name__ == '__main__':
    obj = RecortarRaster()
    gdf = obj.carregar_vetor(os.path.join(os.getcwd(),"amp_modelo.shp"))

    for f in glob.glob(os.getcwd() +"/*.tif"):
        obj.recortar_raster(gdf, os.path.join(os.getcwd(),f))
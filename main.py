#BASES
import requests
from bs4 import BeautifulSoup
import re

#Retirar itens com base no nome da classificação do produto. Ex: Calçados
def remove_products(soup, product_type):
  print(f"")
  all = soup.findAll("product_type",string=re.compile(product_type))
  for item in all:
    print(f"Item de id {item.parent.id.string} removido por ser {item.string}")
    item.parent.decompose()
  return 0

# Função para pegar o item inteiro com base no ID
def get_item(soup, id):
  id_tag = soup.find("id",string=id)
  item_tag = id_tag.parent
  return item_tag

# Função para trocar título do item com base em um dicionário com id e título correto.
def change_title(soup, products):
  print(f"")
  for product in products:
    new_tag = soup.new_tag("title")
    new_tag.string = product["title"]
    item = get_item(soup, product["id"])
    print(f"Título {item.title} substituído por {new_tag}")
    item.title.replace_with(new_tag)


# Função para corrigir o image_link dos itens com base em seu id. 
def repairimgurl(soup,img_ids):
  print(f"")
  for id in img_ids:
    new_tag = soup.new_tag("image_link")
    imageurl = get_item(soup, id).link.string
    imageurl = imageurl.replace("www.loja.com.br/p/","").replace("'", "").replace('"', "")
    new_tag.string = f"www.loja.com.br/imagens/{imageurl}.jpg"
    print(f"Item de id {id} teve seu image_link corrigido para:\n {new_tag}")
    get_item(soup, id).image_link.replace_with(new_tag)

def main():
  #Vamos criar O arquivo local com o feed
  url = "https://storage.googleapis.com/psel-feedmanager/feed.xml"
  response = requests.get(url)
  data = response.content.decode()
  with open("feed.xml", 'w') as f:
    f.write(data)

  soup = BeautifulSoup(data,"xml")

  remove_products(soup, product_type="ados")

  # Como ja foi dado os valores de id que estão com títulos errados e os respectivos títulos certos, podemos montar uma lista básica com os valores para facilitar depois.
  # Essa lista pode ser feita através do excel/sheets com uma grande quantidade de valores para modificar vários ao mesmo tempo.
  products = [
    {
      "id": "198345",
      "title": "Calça legging simples"
    },
    {
      "id": "234123",
      "title": "Óculos de sol - Unissex"
    }
  ]
  #Id dos itens com link de imagens a serem corrigidos
  img_ids = ['564363','939134']

  # Para arrumar inicialmente as tags de título (title) dos ids que estão errados, podemos usar a função abaixo que utiliza os dados 'id' e 'title' da lista products para corrigir.
  change_title(soup,products)

  # Analisando a estrutura, podemos ver que após a tag image_link do item de id 564363 há um texto que não deveria estar lá.
  #   <image_link>"www.loja.com.br/imagens</image_link>gorro-bordado-minimalista.docx",
  # Podemos retirar esse texto utilizando o código:
  get_item(soup, img_ids[0]).image_link.next_sibling.replace_with('')

  # Agora corrigindo os valores de link de imagem errados, utilizamos a função repairimgurl()

  repairimgurl(soup,img_ids)

  # Então reescrevemos as mudanças em um arquivo novo 'output.xml'
  xml = soup.prettify()
  with open("output.xml", "w") as file:
    file.write(xml)

if __name__ == "__main__":
  main()

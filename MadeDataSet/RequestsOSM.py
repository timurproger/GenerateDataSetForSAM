# Этот клас создает текст для запроов
class RequestsOSM():

    # создание и вывод текста для запроса для получения информации о всех обектах
    # которые находяться в выбранной области
    def QueryTextReq(self, tag: str, overpy_bounding_box: str) -> str:
        query_text = f'''
        /*
        This query searches for {tag} features within the specified bounding box.
        */
        [out:json][timeout:25];
        // gather results
        (
          // query part for {tag}
          node["{tag}"]{overpy_bounding_box};
          way["{tag}"]{overpy_bounding_box};
          relation["{tag}"]{overpy_bounding_box};
        );
        // print results
        out body;
        '''
        return query_text

    # Этот текст нужен для получения доп информации
    # о всех обектах которые не вошли в основной запрос
    def ReqTextWays(self, id_ref: int) -> str:
        text = f"""
            way({id_ref});
            (._;>;);
            out body;
            """
        return text